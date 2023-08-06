import json
from typing import Type

import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.graphql import InputDatasetResponse
from dkist_processing_common.models.graphql import RecipeInstanceResponse
from dkist_processing_common.models.graphql import RecipeRunResponse
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.teardown import Teardown


class TeardownTest(Teardown):
    def metadata_store_change_recipe_run_to_completed_successfully(self):
        pass


@pytest.fixture()
def make_mock_GQL_with_configuration():
    def class_generator(configuration: dict):
        class FakeGQLClient:
            def __init__(self, *args, **kwargs):
                pass

            @staticmethod
            def execute_gql_query(**kwargs):
                query_base = kwargs["query_base"]

                if query_base == "recipeRuns":
                    return [
                        RecipeRunResponse(
                            recipeInstanceId=1,
                            recipeInstance=RecipeInstanceResponse(
                                recipeId=1,
                                inputDataset=InputDatasetResponse(
                                    inputDatasetId=1,
                                    isActive=True,
                                    inputDatasetDocument="",
                                ),
                            ),
                            configuration=json.dumps(configuration),
                        ),
                    ]

            @staticmethod
            def execute_gql_mutation(**kwargs):
                ...

        return FakeGQLClient

    return class_generator


@pytest.fixture(scope="session")
def config_with_teardown_enabled() -> dict:
    return {"teardown_enabled": True}


@pytest.fixture(scope="session")
def config_with_teardown_disabled() -> dict:
    return {"teardown_enabled": False}


@pytest.fixture(scope="session")
def config_with_no_teardown() -> dict:
    return dict()


@pytest.fixture(scope="function")
def teardown_task_factory(tmp_path, recipe_run_id):
    def factory(teardown_task_cls: Type[Teardown]):
        number_of_files = 10
        tag_object = Tag.output()
        filenames = [f"file_{filenum}.ext" for filenum in range(number_of_files)]
        with teardown_task_cls(
            recipe_run_id=recipe_run_id,
            workflow_name="workflow_name",
            workflow_version="workflow_version",
        ) as task:
            task.scratch = WorkflowFileSystem(
                recipe_run_id=recipe_run_id,
                scratch_base_path=tmp_path,
            )
            task.scratch.workflow_base_path = tmp_path / str(recipe_run_id)
            for filename in filenames:
                filepath = task.scratch.workflow_base_path / filename
                filepath.touch()
                task.tag(filepath, tag_object)

            return task, filenames, tag_object

    yield factory


def test_purge_data(
    teardown_task_factory, make_mock_GQL_with_configuration, config_with_teardown_enabled, mocker
):
    """
    :Given: A Teardown task with files and tags linked to it and teardown enabled
    :When: Running the task
    :Then: All the files are deleted and the tags are removed
    """
    FakeGQLClass = make_mock_GQL_with_configuration(config_with_teardown_enabled)
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClass
    )
    task, filenames, tag_object = teardown_task_factory(TeardownTest)
    tagged_data = list(task.read(tags=tag_object))
    for filepath in tagged_data:
        assert filepath.exists()
    task()
    for filepath in tagged_data:
        assert not filepath.exists()
    post_purge_tagged_data = list(task.read(tags=tag_object))
    assert len(post_purge_tagged_data) == 0


def test_purge_data_disabled(
    teardown_task_factory, make_mock_GQL_with_configuration, config_with_teardown_disabled, mocker
):
    """
    :Given: A Teardown task with files and tags linked to it and teardown disabled
    :When: Running the task
    :Then: All the files are not deleted and the tags remain
    """
    FakeGQLClass = make_mock_GQL_with_configuration(config_with_teardown_disabled)
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClass
    )
    task, filenames, tag_object = teardown_task_factory(TeardownTest)
    tagged_data = list(task.read(tags=tag_object))
    for filepath in tagged_data:
        assert filepath.exists()
    task()
    for filepath in tagged_data:
        assert filepath.exists()  # still exists
    post_purge_tagged_data = list(task.read(tags=tag_object))
    assert len(post_purge_tagged_data) == len(tagged_data)


def test_purge_data_no_config(
    teardown_task_factory, make_mock_GQL_with_configuration, config_with_no_teardown, mocker
):
    """
    :Given: A Teardown task with files and tags linked and teardown not specified in the configuration
    :When: Running the task
    :Then: All the files are deleted and the tags are removed
    """
    FakeGQLClass = make_mock_GQL_with_configuration(config_with_no_teardown)
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClass
    )
    task, filenames, tag_object = teardown_task_factory(TeardownTest)
    tagged_data = list(task.read(tags=tag_object))
    for filepath in tagged_data:
        assert filepath.exists()
    task()
    for filepath in tagged_data:
        assert not filepath.exists()
    post_purge_tagged_data = list(task.read(tags=tag_object))
    assert len(post_purge_tagged_data) == 0
