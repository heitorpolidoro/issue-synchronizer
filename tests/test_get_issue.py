from src.app import get_issue


def test_same_repository_issue(event, repository):
    get_issue(event.gh, repository, "#123")
    repository.get_issue.assert_called_once_with(123)


def test_other_repository_issue(event, repository):
    gh = event.gh
    get_issue(gh, repository, "owner/other_repository#123")
    gh.get_repo.assert_called_once_with("owner/other_repository")
    gh.get_repo.return_value.get_issue.assert_called_once_with(123)
