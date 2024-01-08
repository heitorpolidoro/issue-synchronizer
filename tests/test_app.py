from unittest.mock import patch

import pytest

from src.app import handle_create_or_edit
from tests.conftest import event


# @pytest.fixture(autouse=True)
# def gh():
#     with patch("app.Github") as gh:
#         yield gh




def test_handle_create_or_edit(event):
    with (
        patch("src.app.handle_tasklist") as handle_tasklist,
        patch("src.app.add_to_project") as add_to_project,
    ):
        handle_create_or_edit(event)
        handle_tasklist.assert_called_once_with(event)
        add_to_project.assert_called_once_with(event)




# def test_handle_issue_sync(event, issue, gh):
#     issue.body = "[sync:repo]"
#     other_repo = Mock()
#     gh.return_value.get_repo.return_value = other_repo
#     with patch("app.sync_issue") as sync_issue:
#         handle_issue(event)
#         sync_issue.assert_called_once_with(issue, other_repo)
#
#
# def test_handle_no_command(event, issue, gh):
#     with patch("app.sync_issue") as sync_issue:
#         handle_issue(event)
#         sync_issue.assert_not_called()
