"""GitHub
"""

import datetime
import os
import sys

from functools import lru_cache

from dotenv import load_dotenv
from github import Github

from github.GithubException import (
    GithubException,
    UnknownObjectException,
)

from semantic_release.history import get_new_version

##
## PUBLIC
##

def get_prerelease_version(repo, bump_level):
    if prerelease := get_latest_prerelease(repo):
        return bump_version(prerelease.title, bump_level)
    if release := get_latest_release(repo):
        return bump_version(release.title, bump_level)

    return bump_version('0.0.0', bump_level)

def run_prerelease(repo, version, pulls):
    try:
        _merge_pull_requests(repo, pulls)

        if prerelease := get_latest_prerelease(repo):
            update_prerelease(prerelease, repo, version)
        else:
            create_prerelease(repo, version)

        return True
    except GithubException as err:
        print(f"\njavelin: {err.data['message']}")
        return False

def run_release(repo):
    if prerelease := get_latest_prerelease(repo):
        prerelease.update_release(
            prerelease.title,
            prerelease.body,
            prerelease=False
        )
    else:
        print('javelin: pre-release not found')
        sys.exit(2)

def get_latest_prerelease(repo):
    for release in repo.get_releases():
        if release.prerelease:
            return release

    return None

def get_latest_release(repo):
    try:
        return repo.get_latest_release()
    except UnknownObjectException:
        return None

def bump_version(version, bump_level):
    if version[0] == 'v':
        version = version[1:]

    new_version = get_new_version(current_version=version,
                                  current_release_version=version,
                                  level_bump=bump_level)

    return f'v{new_version}'

def get_repo(repo_name):
    return _client().get_repo(repo_name)

def fetch_pull_request(repo_name, number):
    try:
        return _client().get_repo(repo_name).get_pull(int(number))
    except UnknownObjectException:
        print('javelin: pull request not found')
        sys.exit(2)

def get_user():
    return _client().get_user()

##
## PRIVATE
##

@lru_cache(maxsize=1)
def _client():
    load_dotenv()

    return Github(os.environ.get('GITHUB_ACCESS_TOKEN'))

def _merge_pull_requests(repo, pulls):
    for pull in pulls:
        print(f'Merging pull request #{pull.number}')

        repo.merge(repo.default_branch, pull.head.sha, f'{pull.title} #{pull.number}')
        repo.get_git_ref(f"heads/{pull.head.ref}").delete()

def create_prerelease(repo, version):
    print(f'Creating pre-release {version}')

    default_branch = repo.get_branch(repo.default_branch)
    release_message = build_release_message(repo, version)

    repo.create_git_tag_and_release(
        version,
        '',
        version,
        release_message,
        default_branch.commit.sha,
        'commit',
        prerelease=True,
    )

def update_prerelease(release, repo, version):
    print(f'Updating pre-release {version}')

    release_message = build_release_message(repo, version)

    release.update_release(
        version,
        release_message,
        prerelease=True,
        tag_name=version,
        target_commitish='main'
    )

def build_release_message(repo, version):
    commits = commits_between_prerelease_and_latest_release(repo, version)
    release_messages = []

    for commit in commits:
        if len(commit.parents) < 2:
            continue

        pulls = commit.get_pulls()

        if pulls.totalCount > 0:
            pull = pulls[0]
            commit_message = pull.title
            commit_url = pull.html_url
        else:
            commit_message = commit.commit.message.partition('\n')[0]
            commit_url = commit.commit.html_url

        release_messages.append(f'- [{commit_message}]({commit_url})')

    release_messages_unique = sorted(set(release_messages), key=release_messages.index)

    return '\n'.join(release_messages_unique)

def commits_between_prerelease_and_latest_release(repo, prerelease_version):
    try:
        tag_name = repo.get_latest_release().tag_name
        tag_commit_sha = repo.get_commit(tag_name).sha
        tag_commit = repo.get_git_commit(tag_commit_sha)

        since = tag_commit.author.date + datetime.timedelta(seconds=1)
    except UnknownObjectException:
        since = datetime.datetime.now() - datetime.timedelta(days=7)

    return repo.get_commits(sha="main", since=since)
