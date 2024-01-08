# import logging
# import re
# from string import Template
# from typing import Optional
#
# from github import Github
# from github.GitCommit import GitCommit
# from github.Issue import Issue
# from github.Repository import Repository
#
# logger = logging.getLogger(__name__)
# SECTION = "ISSUE SUPERVISOR"
# ISSUE_SUPERVISOR_AREA_TEMPLATE = f"""
# <!-- {SECTION}:BEGIN -->
# <!-- Do not remove os change this or the synchronization will stop -->
# [![$command:$repository#$issue_number](https://img.shields.io/badge/$command_title-$issue_ref_title-$color)](https://github.com/$repository/issues/$issue_number)
# <!-- {SECTION}:END -->
# """
# # ISSUE_SUPERVISOR_AREA_TEMPLATE = f"""
# # <!-- {SECTION}:BEGIN -->
# # <!-- Do not remove os change this or the synchronization will stop -->
# # [![synced:$repo#$issue_number](https://img.shields.io/badge/Synched_with-$escaped_repo%23$issue_number-green)](https://github.com/$repo/issues/$issue_number)
# # <!-- {SECTION}:END -->
# # """
#
# SECTION_PATTERN = r"<!-- *$section:BEGIN *-->.*<!-- *$section:END *-->"
#
#
# def get_message_command(text: str, command_prefix: str) -> Optional[str]:
#     """
#     Retrieve the command from the text.
#     The command in the text must be in the format [command_prefix: command]
#
#     :param text: The text.
#     :param command_prefix: The command prefix to look for in the commit message.
#     :return: The extracted command or None if there is no command.
#     """
#     command_pattern = rf"\[{command_prefix}:(.+?)\]"
#     if commands_found := re.findall(command_pattern, text):
#         return commands_found[-1].strip()
#     return None
#
#
# def get_repository_to_sync_from_title(text: str) -> Optional[str]:
#     if repo_name := re.findall(r"\[(.+?)]", text):
#         return repo_name[-1].strip()
#     return None
#
#
# def clear_body(body):
#     return re.sub(
#         Template(SECTION_PATTERN).substitute(section=SECTION),
#         "",
#         body,
#         flags=re.DOTALL,
#     ).strip()
#
#
# def add_badge(issue, command, issue_ref, color):
#     def escape(txt):
#         return txt.replace("-", "--").replace("_", "__").replace("#", "%23")
#
#     command_title = {
#         "tracked-by": "Tracked_by",
#     }
#
#     repository_full_name, issue_number = issue_ref.split("#")
#     body = clear_body(issue.body or "")
#
#     body += "\n" + Template(ISSUE_SUPERVISOR_AREA_TEMPLATE).substitute(
#         command=command,
#         command_title=command_title[command],
#         repository=repository_full_name,
#         issue_number=issue_number,
#         issue_ref_title=escape(f"{repository_full_name}#{issue_number}"),
#         color=color
#     )
#     issue.edit(body=body)
#
#
# def sync_issue(issue: Issue, repository_to: Repository):
#     repository_from = issue.repository
#     logger.info(
#         f"Syncing issue from {repository_from.full_name} to {repository_to.full_name}"
#     )
#     synced_issue = repository_to.create_issue(
#         title=issue.title,
#         body=add_badge(issue.body, repository_from, issue.number),
#     )
#     logger.info(f"Issue {repository_from.full_name}${synced_issue.number} created")
#     issue.edit(body=add_badge(issue.body, repository_to, synced_issue.number))
#     logger.info(f"Issue {repository_to.full_name}${issue.number} updated")
