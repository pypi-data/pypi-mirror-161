"""Subclass of SubmitQuality that causes the correct polcal metrics to build."""
from typing import List
from typing import Optional

from dkist_processing_common.tasks import SubmitQuality


class VispSubmitQuality(SubmitQuality):
    """Subclass just so that the polcal_label_list can be populated."""

    @property
    def polcal_label_list(self) -> Optional[List[str]]:
        """Return labels for beams 1 and 2."""
        return ["Beam 1", "Beam 2"]
