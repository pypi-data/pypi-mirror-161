#!/usr/bin/env python

"""Javelin
"""

import getopt
import sys

import yaml

from .utils import aws
from .utils import github
from .utils import slack
from . import __version__

help_message = """Usage:
  python -m javelin <command> [options]

Commands:
  pre-release                    # Create/update pre-release and deploy Staging:
                                 #   1. Merge specified pull requests
                                 #   2. Create/update GitHub Release with bumped version
                                 #   3. Deploy pre-release to Staging

  release                        # Deploy the latest pre-release to Production

Options:
  -P, [--project=NAME]           # Project name [options: auth_api, auth_web, cloud_api, cloud_web, cms_api]
  -l, [--bump-level=LEVEL]       # Bump level [options: major, minor, patch]
  -p, [--pull-request=NUMBER]    # Pull request number (can be used multiple times)
  -h, [--help]                   # Show this help message and quit
  -v, [--version]                # Show Javelin version number and quit

Examples:
  python -m javelin pre-release -P auth_api -l minor -p 7 -p 11
  python -m javelin pre-release --project=cloud_web --bump-level=patch --pull-request=7
  python -m javelin pre-release -P cms_api -l major --pull-request=11
  python -m javelin release -P auth_web
"""

pr_numbers = []
pulls = []
command = ''
project_name = ''
bump_level = ''

def main(argv):
    _parse_command_arguments(argv)

    match command:
        case 'pre-release':
            _prerelease()
        case 'release':
            _release()
        case '':
            print("javelin: missing command")
            sys.exit(2)
        case _:
            print(f"javelin: invalid command '{command}'")
            sys.exit(2)

def _parse_command_arguments(argv):
    global command
    global project_name
    global bump_level

    try:
        opts, args = getopt.gnu_getopt(argv, 'hvP:l:p:', ['help', 'version', 'project=', 'bump-level=', 'pull-request='])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)

    if len(args) > 0:
        command = args[0]

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(help_message)
            sys.exit()
        if opt in ('-v', '--version'):
            print(__version__)
            sys.exit()
        elif opt in ('-P', '--project'):
            project_name = arg
        elif opt in ('-l', '--bump-level'):
            bump_level = arg
        elif opt in ('-p', '--pull-request'):
            pr_numbers.append(arg)

    pr_numbers.sort()

    if not project_name:
        print("\njavelin: missing project")
        sys.exit(2)

    if command != 'pre-release':
        return

    if not bump_level:
        print("\njavelin: missing bump level")
        sys.exit(2)
    elif bump_level not in ('major', 'minor', 'patch'):
        print("\njavelin: invalid bump level")
        sys.exit(2)

def _prerelease():
    try:
        repo_name = _get_project_repo_name(project_name)
        repo = github.get_repo(repo_name)
        prerelease_version = github.get_prerelease_version(repo, bump_level)

        print('The following actions will be performed:\n')
        print(f'  1. Merge these pull requests into the "{repo.default_branch}" branch:\n')

        for pr_number in pr_numbers:
            pull = github.fetch_pull_request(repo_name, pr_number)
            pulls.append(pull)

            print(f'      #{pull.number}: {pull.title} ({pull.head.ref})')

            if not pull.mergeable or pull.mergeable_state != 'clean':
                print(f"\njavelin: pull request can't be merged ({pull.mergeable_state})")
                sys.exit(2)

        print(f'\n  2. Create a new GitHub Release with version {prerelease_version}')
        print(f'\n  3. Deploy the "{repo.default_branch}" branch to Staging 🚀\n')

        print('\n\033[1mDo you want to continue?\033[0m')
        print('  Only "yes" will be accepted.\n')

        if input('\033[1mEnter a value:\033[0m ') == 'yes':
            github_succeeded = github.run_prerelease(repo, prerelease_version, pulls)

            if github_succeeded:
                aws_succeeded = aws.start_pipeline_execution_and_wait(project_name, 'staging')

                if aws_succeeded:
                    slack.notify_prerelease(project_name, repo, prerelease_version)
                else:
                    slack.notify_prerelease_error(project_name, repo, prerelease_version, pulls)
    except KeyboardInterrupt:
        print('\n\nBye-bye')

def _release():
    try:
        repo_name = _get_project_repo_name(project_name)
        repo = github.get_repo(repo_name)
        latest_prerelease = github.get_latest_prerelease(repo)

        if not latest_prerelease:
            print("javelin: repository doesn't have any pre-releases")
            sys.exit(2)

        release_version = latest_prerelease.title

        print('The following actions will be performed:\n')
        print(f'\n  1. Deploy version {release_version} to Production 🚀\n')
        print('\n\033[1mDo you want to continue?\033[0m')
        print('  Only "yes" will be accepted.\n')

        if input('\033[1mEnter a value:\033[0m ') == 'yes':
            succeeded = aws.start_pipeline_execution_and_wait(project_name, 'production')

            if succeeded:
                github.run_release(repo)
                slack.notify_release(project_name, repo, release_version)
            else:
                slack.notify_release_error(project_name, repo, release_version, pulls)
    except KeyboardInterrupt:
        print('\n\nBye-bye')

def _get_project_repo_name(project_name):
    with open('./config/projects.yml', 'r', encoding='utf-8') as stream:
        try:
            config = yaml.safe_load(stream)

            return config[project_name]['repo_full_names']
        except (KeyError, yaml.YAMLError):
            print("\njavelin: invalid project name")
            sys.exit(2)

if __name__ == '__main__':
    main(sys.argv[1:])
