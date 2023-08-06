import numpy as np
import pytest
from astropy.io import fits
from astropy.time import Time
from dkist_fits_specifications import __version__ as spec_version
from dkist_header_validator import spec214_validator
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tests.conftest import FakeGQLClient

from dkist_processing_visp.tasks.write_l1 import VispWriteL1Frame
from dkist_processing_visp.tests.conftest import VispConstantsDb


@pytest.fixture(
    scope="function",
    params=[("HPLT-TAN", "AWAV"), ("AWAV", "HPLT-TAN")],
    ids=["correct wcs axis order", "incorrect wcs axis order"],
)
def wcs_axis_names(request):
    return request.param


@pytest.fixture(scope="function", params=[1, 4], ids=["stokes I only", "stokes IQUV"])
def write_l1_task(
    recipe_run_id, calibrated_visp_dataset, init_visp_constants_db, request, wcs_axis_names
):
    num_of_stokes_params = request.param
    constants_db = VispConstantsDb(
        INSTRUMENT="VISP",
        AVERAGE_CADENCE=10,
        MINIMUM_CADENCE=10,
        MAXIMUM_CADENCE=10,
        VARIANCE_CADENCE=0,
        NUM_MAP_SCANS=1,
        NUM_RASTER_STEPS=2,
        SPECTRAL_LINE="VISP Ca II H",
        POLARIMETER_MODE="observe_polarimetric"
        if num_of_stokes_params == 4
        else "observe_intensity",
    )
    init_visp_constants_db(recipe_run_id, constants_db)
    with VispWriteL1Frame(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            stokes_params = ["I", "Q", "U", "V"]
            used_stokes_params = []
            hdu = fits.PrimaryHDU(data=np.ones(shape=(128, 128, 1)), header=calibrated_visp_dataset)
            hdul = fits.HDUList([hdu])
            hdul[0].header["CTYPE1"] = wcs_axis_names[0]
            hdul[0].header["CTYPE2"] = wcs_axis_names[1]
            for i in range(num_of_stokes_params):
                task.fits_data_write(
                    hdu_list=hdul,
                    tags=[Tag.calibrated(), Tag.frame(), Tag.stokes(stokes_params[i])],
                )
                used_stokes_params.append(stokes_params[i])
            yield task, used_stokes_params
        except:
            raise
        finally:
            task.constants._purge()
            task.scratch.purge()


def test_write_l1_frame(write_l1_task, mocker, wcs_axis_names):
    """
    :Given: a write L1 task
    :When: running the task
    :Then: no errors are raised
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    task, stokes_params = write_l1_task
    task()
    for stokes_param in stokes_params:
        files = list(task.read(tags=[Tag.frame(), Tag.output(), Tag.stokes(stokes_param)]))
        assert len(files) == 1
        for file in files:
            assert file.exists
            assert spec214_validator.validate(file, extra=False)
            hdu_list = fits.open(file)
            header = hdu_list[1].header
            assert len(hdu_list) == 2  # Primary, CompImage
            assert type(hdu_list[0]) is fits.PrimaryHDU
            assert type(hdu_list[1]) is fits.CompImageHDU
            assert header["DAAXES"] == 2
            if len(stokes_params) == 1:
                assert "DNAXIS4" not in header
                assert header["DNAXIS"] == 3
                assert header["DEAXES"] == 1
            else:
                assert header["DNAXIS4"] == 4
                assert header["DNAXIS"] == 4
                assert header["DEAXES"] == 2
            assert header["INFO_URL"] == task.docs_base_url
            assert header["HEADVERS"] == spec_version
            assert (
                header["HEAD_URL"]
                == f"{task.docs_base_url}/projects/data-products/en/v{spec_version}"
            )
            calvers = task._get_version_from_module_name()
            assert header["CALVERS"] == calvers
            assert (
                header["CAL_URL"]
                == f"{task.docs_base_url}/projects/{task.constants.instrument.lower()}/en/v{calvers}/{task.workflow_name}.html"
            )
            calibrated_file = next(
                task.read(tags=[Tag.frame(), Tag.calibrated(), Tag.stokes(stokes_param)])
            )
            cal_header = fits.open(calibrated_file)[0].header

            # Make sure we didn't overwrite pre-computed DATE-BEG and DATE-END keys
            assert header["DATE-BEG"] == cal_header["DATE-BEG"]
            assert header["DATE-END"] == cal_header["DATE-END"]
            date_avg = (
                (Time(header["DATE-END"], precision=6) - Time(header["DATE-BEG"], precision=6)) / 2
                + Time(header["DATE-BEG"], precision=6)
            ).isot
            assert header["DATE-AVG"] == date_avg

            # Check WCS axes are the right way around by checking the CTYPEs
            assert header["CTYPE1"] == "HPLT-TAN"
            assert header["CTYPE2"] == "AWAV"
            assert header["CTYPE3"] == "HPLN-TAN"
