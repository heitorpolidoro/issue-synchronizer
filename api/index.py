import json
import logging
import os
import re
from http.server import BaseHTTPRequestHandler
from string import Template
from types import SimpleNamespace

from github import Github, GithubIntegration

logging.basicConfig(level=logging.INFO)

YOUR_APP_ID = 684296

COMMANDS = ["sync", "synced"]
ISSUE_SYNCHRONIZER_AREA_TEMPLATE = """
<!-- ISSUE SYNCHRONIZED:BEGIN -->
[![synced:$repo#$issue_number](https://img.shields.io/badge/Synched_with-$escaped_repo%23$issue_number-green)](https://github.com/$repo/issues/$issue_number)
<!-- ISSUE SYNCHRONIZED:END-->
"""


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


def clear_body(body, command_prefixes):
    command_prefix = "sync"
    command_pattern = rf"\[{command_prefix}:(.+?)\]"
    return re.sub(command_pattern, "", body)


# def replace_section(readme_content, section, content):
#     if not re.search(rf"<!-- {section}: starts -->.*<!-- {section}: ends -->", readme_content, flags=re.DOTALL):
#         logging.warning(
#             f"Section {section} no found in README.md\n<!-- {section}: starts -->\n<!-- {section}: ends -->")
#     return re.sub(rf"<!-- {section}: starts -->.*<!-- {section}: ends -->",
#                   f"<!-- {section}: starts -->\n{content}\n<!-- {section}: ends -->", readme_content, flags=re.DOTALL)

def add_badge(body, repo, issue_number):
    repo_full_name = repo.full_name
    body = clear_body(body, COMMANDS)
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
    issue.edit(body=add_badge(issue.body, repo_to, synced_issue.number))


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
        print(payload.action)
        if payload.issue.user.type != "Bot":
            if issue := payload.issue:
                if payload.action == "opened":
                    logging.info("Issue opened: " + issue.title)
                    repo_to_sync = get_command(issue.body, "sync")
                    if repo_to_sync:
                        token = get_token(payload.installation.id)
                        repo_from = Github(token).get_repo(payload.repository.full_name)
                        repo_to = Github(token).get_repo(repo_to_sync)
                        gh_issue = repo_from.get_issue(issue.number)
                        create_synced_issue(gh_issue, repo_from, repo_to)

        # handle payload here
        # print(payload)

        self.send_response(201)
        self.end_headers()
