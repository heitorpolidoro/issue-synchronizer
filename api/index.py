import json
import logging
import os
import re
from functools import lru_cache
from http.server import BaseHTTPRequestHandler
from string import Template
from types import SimpleNamespace

from github import Github, GithubIntegration

logging.basicConfig(level=logging.INFO)

YOUR_APP_ID = 684296

SECTION = "ISSUE SYNCHRONIZER"
ISSUE_SYNCHRONIZER_AREA_TEMPLATE = f"""
<!-- {SECTION}:BEGIN -->
<!-- Do not remove os change this or the synchronization will stop -->
[![synced:$repo#$issue_number](https://img.shields.io/badge/Synched_with-$escaped_repo%23$issue_number-green)](https://github.com/$repo/issues/$issue_number)
<!-- {SECTION}:END -->
"""

SECTION_PATTERN = r"<!-- *$section:BEGIN *-->.*<!-- *$section:END *-->"


def dict_to_obj(d: dict) -> SimpleNamespace:
    if isinstance(d, dict):
        return SimpleNamespace(**{k: dict_to_obj(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [dict_to_obj(v) for v in d]
    else:
        return d


# noinspection PyPep8Naming
def get_command(body, command_prefix):
    command_pattern = rf"\[{command_prefix}:(.+?)\]"
    commands_found = re.findall(command_pattern, body)
    if commands_found:
        return commands_found[-1].strip()

    return None


def clear_body(body):
    command_prefix = "sync"
    command_pattern = rf"\[{command_prefix}:(.+?)\]"
    return re.sub(
        Template(SECTION_PATTERN).substitute(section=SECTION),
        "",
        re.sub(command_pattern, "", body),
        flags=re.DOTALL).strip()


def add_badge(body, repo, issue_number):
    repo_full_name = repo.full_name
    body = clear_body(body)
    escaped_repo = repo_full_name.replace("-", "--").replace("_", "__")
    body += "\n" + Template(ISSUE_SYNCHRONIZER_AREA_TEMPLATE).substitute(repo=repo_full_name, issue_number=issue_number,
                                                                         escaped_repo=escaped_repo)
    return body


def create_synced_issue(issue, repo_from, repo_to):
    logging.info(f"Syncing issue from {repo_from.full_name} to {repo_to.full_name}")

    synced_issue = repo_to.create_issue(
        title=issue.title,
        body=add_badge(issue.body, repo_from, issue.number),
    )
    logging.info(f"Issue {repo_from.full_name}${synced_issue.number} created")
    issue.edit(body=add_badge(issue.body, repo_to, synced_issue.number))
    logging.info(f"Issue {repo_to.full_name}${issue.number} updated")


@lru_cache
def get_token(installation_id):
    if not (private_key := os.getenv("PRIVATE_KEY")):
        with open("private-key.pem", "rb") as key_file:
            private_key = key_file.read().decode()

    integration = GithubIntegration(YOUR_APP_ID, private_key)

    # Get the installation access token
    return integration.get_access_token(installation_id).token


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('Issue Synchronizer up and running!\n'.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        payload = dict_to_obj(json.loads(body))
        action = payload.action
        if payload.sender.type != "Bot":
            if issue := payload.issue:
                logging.info(f"Issue {action}: {payload.repository.full_name}#{issue.number}")
                if repo_to_sync := get_command(issue.body, "sync"):
                    repo_from = get_repo(payload.repository.full_name, payload.installation.id)
                    repo_to = get_repo(repo_to_sync, payload.installation.id)
                    gh_issue = repo_from.get_issue(issue.number)
                    create_synced_issue(gh_issue, repo_from, repo_to)
                else:
                    if issue_to_sync := get_command(issue.body, "synced"):
                        repo_to_sync, issue_number = issue_to_sync.split("#")
                        repo_to = get_repo(repo_to_sync, payload.installation.id)
                        gh_issue = repo_to.get_issue(int(issue_number))
                        logging.info(f"Updating issue {repo_to.full_name}#{gh_issue.number}")
                        if action == "edited":
                            changes = {}
                            for changed_field in payload.changes.__dict__.keys():
                                logging.info(f"Changed field: {changed_field}")
                                changes[changed_field] = getattr(issue, changed_field)
                                if changed_field == "body":
                                    changes[changed_field] = add_badge(
                                        clear_body(changes[changed_field]),
                                        payload.repository,
                                        issue.number)
                            gh_issue.edit(**changes)
                        elif action == "labeled":
                            gh_issue.add_to_labels(payload.label.name)
                        elif action == "unlabeled":
                            gh_issue.remove_from_labels(payload.label.name)
                        elif action == "assigned":
                            gh_issue.add_to_assignees(payload.assignee.login)
                        elif action == "unassigned":
                            gh_issue.remove_from_assignees(payload.assignee.login)
                        elif action == "closed":
                            gh_issue.edit(state="closed", state_reason=issue.state_reason)
                        elif action == "reopened":
                            gh_issue.edit(state="open")
                        else:
                            logging.info(f"Ignoring action {action}")
                    elif re.search(Template(SECTION_PATTERN).substitute(section=SECTION),
                                   getattr(payload.changes.body, "from"), flags=re.DOTALL):
                        issue_to_sync = get_command(getattr(payload.changes.body, "from"), "synced")
                        repo_to_sync, issue_number = issue_to_sync.split("#")
                        repo_to = get_repo(repo_to_sync, payload.installation.id)
                        gh_issue = repo_to.get_issue(int(issue_number))

                        logging.warning(
                            f"Issue Synchronizer Badge removed from {payload.repository.full_name}#{issue.number}!"
                            f" Removing from {repo_to.full_name}#{gh_issue.number}"
                        )
                        gh_issue.edit(body=clear_body(gh_issue.body))
                        warning_message = (":warning: Issue Synchronizer Badge removed!\n"
                                           "Lost synchronization with $issue")
                        gh_issue.create_comment(Template(warning_message).substitute(
                            issue=f"{payload.repository.full_name}#{issue.number}"))
                        repo_from = get_repo(payload.repository.full_name, payload.installation.id)
                        gh_issue_from = repo_from.get_issue(issue.number)
                        gh_issue_from.create_comment(
                            Template(warning_message).substitute(issue=f"{repo_to.full_name}#{gh_issue.number}"))

        self.send_response(201)
        self.end_headers()


def get_repo(full_name, installation_id):
    token = get_token(installation_id)
    return Github(token).get_repo(full_name)
