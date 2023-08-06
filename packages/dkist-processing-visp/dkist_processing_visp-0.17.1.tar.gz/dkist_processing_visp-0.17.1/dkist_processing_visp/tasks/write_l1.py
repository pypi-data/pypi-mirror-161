"""Visp write L1 task."""
import logging
import uuid
from datetime import datetime
from typing import Literal

import numpy as np
from astropy.io import fits
from astropy.time import Time
from dkist_processing_common.tasks import WriteL1Frame

from dkist_processing_visp.models.constants import VispConstants


class VispWriteL1Frame(WriteL1Frame):
    """
    Task class for writing out calibrated l1 ViSP frames.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs
    """

    @property
    def constants_model_class(self):
        """Get Visp pipeline constants."""
        return VispConstants

    def add_dataset_headers(
        self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]
    ) -> fits.Header:
        """
        Add the VISP specific dataset headers to L1 FITS files.

        Parameters
        ----------
        header : fits.Header
            calibrated data header

        stokes :
            stokes parameter

        Returns
        -------
        fits.Header
            calibrated header with correctly written l1 headers
        """
        # Correct the headers for the number of map and scan steps per map due to potential observation aborts
        header["VSPNMAPS"] = self.constants.num_map_scans
        header["VSPNSTP"] = self.constants.num_raster_steps

        if stokes.upper() not in self.constants.stokes_params:
            raise ValueError("The stokes parameter must be one of I, Q, U, V")

        # ---Spatial 1---
        header["DNAXIS1"] = header["NAXIS1"]
        header["DTYPE1"] = "SPATIAL"
        header["DPNAME1"] = "spatial along slit"
        header["DWNAME1"] = "helioprojective latitude"
        header["DUNIT1"] = header["CUNIT1"]

        # ---Spectral---
        header["DNAXIS2"] = header["NAXIS2"]
        header["DTYPE2"] = "SPECTRAL"
        header["DPNAME2"] = "dispersion axis"
        header["DWNAME2"] = "wavelength"
        header["DUNIT2"] = header["CUNIT2"]

        # ---Spatial 2---
        header["DNAXIS3"] = self.constants.num_raster_steps
        header["DTYPE3"] = "SPATIAL"
        header["DPNAME3"] = "raster scan step number"
        header["DWNAME3"] = "helioprojective longitude"
        header["DUNIT3"] = header["CUNIT3"]
        # Raster position in dataset
        header["DINDEX3"] = (
            header["VSPSTP"] + 1
        )  # Current position in raster scan which counts from zero

        # Set the base number of dataset axes to 3
        num_axis = 3

        # ---Temporal---
        if self.constants.num_map_scans > 1:
            num_axis += 1
            header[
                f"DNAXIS{num_axis}"
            ] = self.constants.num_map_scans  # total number of raster scans in the dataset
            header[f"DTYPE{num_axis}"] = "TEMPORAL"
            header[f"DPNAME{num_axis}"] = "raster map repeat number"
            header[f"DWNAME{num_axis}"] = "time"
            header[f"DUNIT{num_axis}"] = "s"
            # Temporal position in dataset
            header[f"DINDEX{num_axis}"] = header["VSPMAP"]  # Current raster scan

        # ---Stokes---
        if self.constants.correct_for_polarization:
            num_axis += 1
            header[f"DNAXIS{num_axis}"] = 4  # I, Q, U, V
            header[f"DTYPE{num_axis}"] = "STOKES"
            header[f"DPNAME{num_axis}"] = "polarization state"
            header[f"DWNAME{num_axis}"] = "polarization state"
            header[f"DUNIT{num_axis}"] = ""
            # Stokes position in dataset - stokes axis goes from 1-4
            header[f"DINDEX{num_axis}"] = self.constants.stokes_params.index(stokes.upper()) + 1

        else:
            logging.info("Spectrographic data detected. Not adding DNAXIS information.")

        header["DNAXIS"] = num_axis
        header["DAAXES"] = 2  # Spectral, spatial
        header["DEAXES"] = num_axis - 2  # Total - detector axes

        # VISP has a wavelength axis in the frame and so FRAMEWAV is hard to define. Use LINEWAV.
        header["LEVEL"] = 1
        header["WAVEBAND"] = self.constants.spectral_line
        header["WAVEUNIT"] = -9  # nanometers
        header["WAVEREF"] = "Air"
        # The wavemin and wavemax assume that all frames in a dataset have identical wavelength axes
        header["WAVEMIN"] = header["CRVAL1"] - (header["CRPIX1"] * header["CDELT1"])
        header["WAVEMAX"] = header["CRVAL1"] + (
            (header["NAXIS1"] - header["CRPIX1"]) * header["CDELT1"]
        )

        # Binning headers
        header["NBIN1"] = 1
        header["NBIN2"] = 1
        header["NBIN3"] = 1
        header["NBIN"] = header["NBIN1"] * header["NBIN2"] * header["NBIN3"]

        return header

    def _replace_header_values(self, header: fits.Header, data: np.ndarray) -> fits.Header:
        """
        Replace the FILE_ID and DATE keywords with new values.

        This is overloaded from dkist-processing-common because DATE-END is computed correctly in ScienceCalibration
        and the *-common version of this method would overwrite that key.
        """
        header["FILE_ID"] = uuid.uuid4().hex
        header["DATE"] = Time(datetime.now().isoformat(), precision=6).fits
        # Remove BZERO and BSCALE as their value should be recalculated by astropy upon fits write
        header.pop("BZERO", None)
        header.pop("BSCALE", None)
        # Make sure that NAXIS is set to the shape of the data in case of squeezing
        header["NAXIS"] = len(data.shape)
        # Check that the WCS headers are in the right order
        if header["CTYPE1"] == "AWAV":  # Then the order is wrong
            header = self.transpose_wcs_keys(header=header)
        return header

    @staticmethod
    def transpose_wcs_keys(header: fits.Header) -> fits.Header:
        """
        In early DKIST operations, some WCS keys and the PCi_j matrix were incorrectly ordered.

        This function transposes them to reverse it.
        """
        logging.info(f"Transposing axes 1 and 2 of the WCS headers")

        # What keys need to be transposed? Substitute "n" for the axis number.
        # All FITS keywords are supposed to be uppercase so using lowercase "n" should be OK
        # CRPIXn is excluded from this list as it is observed to be in the
        # correct order already (does not need transposing.)
        key_list = [
            "CRDATEn",
            "CRVALn",
            "CDELTn",
            "CUNITn",
            "CTYPEn",
        ]

        # Gather the values from the key_list keywords and swap them in place
        for key in key_list:
            for suffix in ["", "A"]:
                key_1 = f"{key}{suffix}".replace("n", "1")
                key_2 = f"{key}{suffix}".replace("n", "2")
                try:
                    header[key_1], header[key_2] = header[key_2], header[key_1]
                except KeyError:  # The "A" variant of keywords are not required
                    logging.info(
                        f"Keywords {key_1} and {key_2} were not switched as they do not exist in this frame."
                    )

        # The PC matrix is observed to be in a different order.
        # It is in the lt, ln, wave order, when we want it in the lt, wave, ln order.
        for n in range(1, 4):
            header[f"PC2_{n}"], header[f"PC3_{n}"] = header[f"PC3_{n}"], header[f"PC2_{n}"]
        # Note also that the reordered value of PC2_2 (i.e. wave) is probably wrong and should be one

        return header
