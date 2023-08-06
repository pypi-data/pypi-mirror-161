import random
import string

import pytest
from hypothesis import given
from hypothesis.strategies import integers

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.constants import ConstantsBase


@pytest.fixture(scope="session")
def test_dict() -> dict:
    data = {
        "KEY 0": random.randint(-(2**51), 2**51),
        "KEY 1": random.random(),
        "KEY 2": "".join(
            [random.choice(string.ascii_letters) for _ in range(random.randint(0, 512))]
        ),
    }
    return data


@pytest.fixture()
def test_constants_db(test_dict, constants_db):
    for key, value in test_dict.items():
        constants_db[key] = value

    return constants_db


class ConstantsFinal(ConstantsBase):
    @property
    def key_0(self) -> int:
        return self._db_dict["KEY 0"]

    @property
    def key_1_squared(self) -> float:
        return self._db_dict["KEY 1"] ** 2  # Just to show that you can do whatever you want


def test_constants_db_as_dict(test_constants_db, test_dict):
    """
    Given: a ConstantsDb object and a python dictionary
    When: treating the ConstantsDb object as a dict for getting and setting
    Then: the ConstantsDb object behaves like a dictionary
    """
    assert len(test_constants_db) == len(test_dict)
    assert sorted(list(test_constants_db)) == sorted(list(test_dict.keys()))
    for key, value in test_dict.items():
        assert test_constants_db[key] == value


def test_key_exists(constants_db):
    """
    Given: a populated ConstantsDb object
    When: trying to set a key that already exists
    Then: an error is raised
    """
    constants_db["foo"] = "baz"
    with pytest.raises(ValueError):
        constants_db["foo"] = "baz2: electric bogaloo"


def test_replace_key(constants_db):
    """
    Given: a populated ConstantsDb object
    When: a constant key is deleted
    Then: the key is removed and no longer exists in the ConstantsDb object
    """
    constants_db["foo"] = "baz"
    del constants_db["foo"]
    assert "foo" not in constants_db
    constants_db["foo"] = "baz3: tokyo drift"
    assert constants_db["foo"] == "baz3: tokyo drift"


def test_key_does_not_exist(constants_db):
    """
    Given: a ConstantsDb object
    When: trying to get a constant value that doesn't exist
    Then: an error is raised
    """
    with pytest.raises(KeyError):
        _ = constants_db["foo"]


def test_constants_subclass(test_constants_db, recipe_run_id):
    """
    Given: a subclass of ConstantsBase and a ConstantsDb object
    When: initializing the ConstantsBase class with the ConstantsDb object
    Then: the subclass contains the correct properties
    """
    obj = ConstantsFinal(recipe_run_id=recipe_run_id, task_name="foo")
    obj._db_dict = test_constants_db
    assert obj.key_0 == test_constants_db["KEY 0"]
    assert obj.key_1_squared == test_constants_db["KEY 1"] ** 2


@given(
    id_x=integers(min_value=1, max_value=2147483647),
    id_y=integers(min_value=1, max_value=2147483647),
)
def test_dataset_id_uniquely_generated_from_recipe_run_id(id_x, id_y):
    """
    Given: 2 integers > 0
    When: 2 tasks are created using the integers for each of the tasks
    Then: The dataset_id for each class compares the same as the integers compare
       e.g. (1 == 1) is (dataset_id(1) == dataset_id(1))  : True is True
       e.g. (1 == 2) == (dataset_id(1) == dataset_id(2))  : False is False
    """
    expected = id_x == id_y
    constants_x = ConstantsBase(recipe_run_id=id_x, task_name="foo")
    constants_y = ConstantsBase(recipe_run_id=id_y, task_name="foo")
    actual = constants_x.dataset_id == constants_y.dataset_id
    assert expected is actual


@given(id_x=integers(min_value=1, max_value=2147483647))
def test_dataset_id_from_recipe_run_id_produces_the_same_value(id_x):
    """
    Given: an integer > 0
    When: 2 tasks are created using the same integer for each of the tasks
    Then: The dataset_id for each class are equal
    """
    constants_x = ConstantsBase(recipe_run_id=id_x, task_name="foo")
    constants_y = ConstantsBase(recipe_run_id=id_x, task_name="foo")
    assert constants_x.dataset_id == constants_y.dataset_id
