from src.app import get_tasklist


def test_handle_tasklist():
    event_body = """Some body
- [ ] not checked task
- [x] checked task
ignored
- [ ] [repo] other task
"""
    tasks = get_tasklist(event_body)
    assert tasks == [
        (False, "not checked task"),
        (True, "checked task"),
        (False, "[repo] other task"),
    ]
