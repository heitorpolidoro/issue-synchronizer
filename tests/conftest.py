from unittest.mock import Mock

import pytest


@pytest.fixture
def issue():
    """
    This fixture returns a mock issue object with default values for the attributes.
    :return: Mocked Issue
    """
    return Mock(title="issue title")


@pytest.fixture
def repository():
    """
    This fixture returns a mock repository object with default values for the attributes.
    :return: Mocked Repository
    """
    return Mock()


@pytest.fixture
def event(issue, repository):
    """
    This fixture returns a mocked event object with default values for the attributes.
    :return: Mocked Event
    """
    return Mock(
        issue=issue,
        repository=repository,
        ref="issue-42",
        branches=[Mock(name="issue-42")],
    )
