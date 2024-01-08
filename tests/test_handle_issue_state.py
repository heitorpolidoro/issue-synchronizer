from unittest.mock import patch

import pytest

from src.app import handle_tasklist, handle_issue_state


@pytest.fixture
def get_tasklist_mock():
    with patch("src.app.get_tasklist") as mock:
        yield mock


def test_close_issue_when_task_is_checked_and_issue_is_open(issue):
    issue.state = "open"
    handle_issue_state(True, issue)
    issue.edit.assert_called_once_with(state="closed")


def test_do_nothing_issue_when_task_is_checked_and_issue_is_closed(issue):
    issue.state = "closed"
    handle_issue_state(True, issue)
    issue.edit.assert_not_called()


def test_open_issue_when_task_is_not_checked_and_issue_is_closed(issue):
    issue.state = "closed"
    handle_issue_state(False, issue)
    issue.edit.assert_called_once_with(state="open")


def test_do_nothing_issue_when_task_is_not_checked_and_issue_is_closed(issue):
    issue.state = "open"
    handle_issue_state(False, issue)
    issue.edit.assert_not_called()
