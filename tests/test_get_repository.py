from unittest.mock import Mock

import pytest
from github import UnknownObjectException

from src.app import get_repository


@pytest.fixture
def mocked_get_repo(repository):
    def gh_get_repo(repository_name):
        if repository_name == "onwer/repository":
            return repository
        else:
            raise UnknownObjectException(404)

    return gh_get_repo


@pytest.fixture
def gh(mocked_get_repo):
    """
    This fixture returns a mock GitHub object with default values for the attributes.
    :return: Mocked GitHub
    """
    mock = Mock()
    mock.get_repo = mocked_get_repo
    return mock


def test_get_full_name(gh, repository):
    assert get_repository(gh, "onwer/repository") == repository


def test_get_partial_name(gh, repository):
    assert get_repository(gh, "repository", "onwer") == repository


def test_not_a_repository(gh, repository):
    assert get_repository(gh, "not a repository", "onwer") is None
