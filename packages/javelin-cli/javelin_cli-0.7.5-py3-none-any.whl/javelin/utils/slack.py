"""Slack
"""

import sys
import yaml

from slack_sdk.webhook import WebhookClient
from . import github

##
## PUBLIC
##

def notify_prerelease(project_name, repo, prerelease_version):
    url = _get_project_webhook_url(project_name)
    text = notify_prerelease_text(project_name, repo, prerelease_version)

    _send_message(url, text)

def notify_prerelease_text(project_name, repo, prerelease_version):
    commits = github.commits_between_prerelease_and_latest_release(repo, prerelease_version)

    message = f"""
<!here> *{project_name.upper()} pre-release :rocket:*

<https://github.com/{repo.full_name}/releases/tag/{prerelease_version}|*{prerelease_version}*>
{_message_links(commits)}

{_message_footer()}
    """

    return message

def notify_release(project_name, repo, release_version):
    url = _get_project_webhook_url(project_name)
    text = notify_release_text(project_name, repo, release_version)

    _send_message(url, text)

def notify_release_text(project_name, repo, release_version):
    commits = github.commits_between_prerelease_and_latest_release(repo, release_version)

    message = f"""
<!here> *{project_name.upper()} release :rocket:*

<https://github.com/{repo.full_name}/releases/tag/{release_version}|*{release_version}*>
{_message_links(commits)}

{_message_footer()}
    """

    return message

def _message_links(commits):
    message_links = []

    for commit in commits:
        if len(commit.parents) < 2:
            continue

        commit_url = commit.commit.html_url
        pulls = commit.get_pulls()

        if pulls.totalCount > 0:
            pull = pulls[0]
            commit_message = pull.title
            commit_url = pull.html_url
            author_login = pull.user.login
        else:
            commit_message = commit.commit.message.partition('\n')[0]
            author_login = commit.author.login

        message_links.append(f'- <{commit_url}|{commit_message}> ({_get_slack_user_id(author_login)})')

    message_links_unique = sorted(set(message_links), key=message_links.index)

    return '\n'.join(message_links_unique)

def notify_prerelease_error(project_name, repo, version, pulls):
    message_links = ''

    for pull in pulls:
        message_links += f'- <https://github.com/{repo.full_name}/pull/{pull.number}|{pull.title}> ({_get_slack_user_id(pull.user.login)})\n'

    text = f"""
<!here> *{project_name.upper()} pre-release FAILED :warning:*

<https://github.com/{repo.full_name}/releases/tag/{version}|*{version}*>
{message_links}

{_message_footer()}
    """

    url = _get_project_webhook_url(project_name)

    _send_message(url, text)

def notify_release_error(project_name, repo, version, pulls):
    message_links = ''

    for pull in pulls:
        message_links += f'- <https://github.com/{repo.full_name}/pull/{pull.number}|{pull.title}> ({_get_slack_user_id(pull.user.login)})\n'

    text = f"""
<!here> *{project_name.upper()} release FAILED :warning:*

<https://github.com/{repo.full_name}/releases/tag/{version}|*{version}*>
{message_links}

{_message_footer()}
    """

    url = _get_project_webhook_url(project_name)

    _send_message(url, text)

##
## PRIVATE
##

def _get_slack_user_id(github_login):
    try:
        return {
            'akoarum': '<@U012ZR4QR0U>',
            'djGrill': '<@U8JLQAY8Y>',
            'fksgshota': '<@UM64SRT7V>',
            'KeisukeMoriyama': '<@U015NQ2D0N5>',
            'koheishinpuku': '<@U017T099B7F>',
            'masaki-ono': '<@U012ZLA3WV8>',
            'nakahide2': '<@U02CWB6JK>',
            'oxo-yuta': '<@U01AVSEMVST>',
            'pandaulait': '<@U02RAMZ9J1W>',
            'qst-exe': '<@UUKP09X1B>',
            'shin73': '<@U02CVD90R>',
            'vladinomo': '<@U124WEULF>',
            'yoannes': '<@UQ3U5V8KY>',
        }[github_login]
    except KeyError:
        return github_login

def _get_project_webhook_url(project_name):
    with open('./config/projects.yml', 'r', encoding='utf-8') as stream:
        try:
            config = yaml.safe_load(stream)

            return config[project_name]['slack_webhook_url']
        except (KeyError, yaml.YAMLError):
            print("\njavelin: invalid project name")
            sys.exit(2)

def _message_footer():
    current_user_github_login = github.get_user().login

    return f'Via *Javelin* by {_get_slack_user_id(current_user_github_login)}'

def _send_message(url, text):
    WebhookClient(url).send(text=text)
