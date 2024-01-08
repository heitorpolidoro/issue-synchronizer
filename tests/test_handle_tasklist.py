from unittest.mock import patch, ANY

import pytest

from src.app import handle_tasklist

GET_TASKLIST = "src.app.get_tasklist"
GET_REPOSITORY = "src.app.get_repository"


@pytest.fixture(autouse=True)
def get_issue_mock():
    with patch("src.app.get_issue", return_value=None) as get_issue:
        yield get_issue


def test_create_in_same_repository_with_other_title(event, issue, repository):
    with patch(GET_TASKLIST, return_value=[(False, "local")]), patch(
        GET_REPOSITORY, return_value=None
    ):
        handle_tasklist(event)
        repository.create_issue.assert_called_once_with(title="local")


def test_create_in_other_repository_with_same_title(event, issue, repository):
    with patch(GET_TASKLIST, return_value=[(False, "other_repo")]), patch(
        GET_REPOSITORY, return_value=repository
    ) as get_repository:
        handle_tasklist(event)
        get_repository.assert_called_once_with(ANY, "other_repo")
        repository.create_issue.assert_called_once_with(title="issue title")


def test_create_in_other_repository_with_other_title(event, issue, repository):
    with patch(GET_TASKLIST, return_value=[(False, "[other_repo] other title")]), patch(
        GET_REPOSITORY, return_value=repository
    ) as get_repository:
        handle_tasklist(event)
        get_repository.assert_called_once_with(ANY, "other_repo")
        repository.create_issue.assert_called_once_with(title="other title")
