"""Task(s) for the clean up tasks at the conclusion of a processing pipeline."""
import logging

from dkist_processing_common.tasks.base import WorkflowTaskBase


__all__ = ["Teardown"]


logger = logging.getLogger(__name__)


class Teardown(WorkflowTaskBase):
    """
    Changes the status of the recipe run to "COMPLETEDSUCCESSFULLY".

    Deletes the scratch directory containing all data from this pipeline run
    """

    @property
    def teardown_enabled(self) -> bool:
        """Recipe run configuration indicating if data should be removed at the end of a run."""
        return self.metadata_store_recipe_run_configuration().get("teardown_enabled", True)

    def run(self) -> None:
        """Run method for Teardown class."""
        with self.apm_task_step("Change Recipe Run to Complete Successfully"):
            self.metadata_store_change_recipe_run_to_completed_successfully()

        if not self.teardown_enabled:
            with self.apm_task_step(f"Skip Teardown"):
                logger.info(f"Data and tags for recipe run {self.recipe_run_id} NOT removed")
                return

        logger.info(f"Removing data and tags for recipe run {self.recipe_run_id}")

        with self.apm_task_step("Remove Data and Tags"):
            self.scratch.purge()

        with self.apm_task_step("Remove Constants"):
            self.constants._purge()
