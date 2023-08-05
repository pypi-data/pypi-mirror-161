import pytest

from dkist_processing_visp.tasks.l1_output_data import VispSubmitQuality


@pytest.fixture
def visp_submit_quality_task(tmp_path, recipe_run_id):

    with VispSubmitQuality(
        recipe_run_id=recipe_run_id, workflow_name="visp_submit_quality", workflow_version="VX.Y"
    ) as task:
        yield task
        task.scratch.purge()
        task.constants._purge()


@pytest.fixture
def build_report_mock(mocker):
    yield mocker.patch(
        "dkist_processing_common.tasks.mixin.quality.QualityMixin.quality_build_report",
        autospec=True,
    )


def test_correct_polcal_label_list(visp_submit_quality_task, build_report_mock, mocker):
    """
    Given: A VispSubmitQuality task
    When: Calling the task
    Then: The correct polcal_label_list property is passed to .build_report
    """
    task = visp_submit_quality_task

    # We don't care about this
    mocker.patch(
        "dkist_processing_visp.tasks.l1_output_data.VispSubmitQuality.metadata_store_add_quality_report"
    )

    task()
    build_report_mock.assert_called_once_with(task, polcal_label_list=["Beam 1", "Beam 2"])
