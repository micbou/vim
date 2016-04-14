#!/usr/bin/env python

import argparse
import os
import subprocess
import re
import textwrap
from distutils.spawn import find_executable

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

VIM_COMMIT = re.compile('patch (?P<version>.*) '
                        'Problem:(?:\s+)(?P<problem>.*) '
                        'Solution:(?:\s+)(?P<solution>.*)')
CHANGELOG_LINE = '{version}: {problem} {solution}'


def replace_multiplespaces_by_one(string):
    return ' '.join(string.split())


def format_logs(patches):
    formatted_patches = []
    for patch in patches.splitlines():
        match = VIM_COMMIT.match(patch)
        if match:
            problem = replace_multiplespaces_by_one(match.group('problem'))
            solution = replace_multiplespaces_by_one(match.group('solution'))
            formatted_patch = CHANGELOG_LINE.format(
              version=match.group('version'),
              problem=problem,
              solution=solution)
            formatted_patches.append(formatted_patch)
    logs = []
    for patch in reversed(formatted_patches):
        log = textwrap.wrap(patch)
        formatted_log = ['- ' + log[0]]
        for line in log[1:]:
            formatted_log.append('  ' + line)
        logs.extend(formatted_log)
    return logs


def deploy(args):
    git = find_executable('git')
    if git is None:
        raise RuntimeError('git tool not found.')

    # Move to script folder
    os.chdir(SCRIPT_DIR)

    # Switch to master branch
    subprocess.check_call([git, 'checkout', 'master'])

    # Fetch upstream remote
    subprocess.check_call([git, 'fetch', 'upstream'])

    # Format logs
    patches = subprocess.check_output(
      [git, 'log', '--pretty=format:%s',
       'master..upstream/master']).strip().decode('utf8')
    logs = format_logs(patches)

    # Merge upstream master branch
    subprocess.check_call([git, 'merge', '--no-edit', 'upstream/master'])

    # Get the latest tag
    latest_commit = subprocess.check_output(
        [git, 'rev-list', '--tags', '--max-count=1']).strip().decode('utf8')
    latest_tag = subprocess.check_output(
        [git, 'describe', '--tags', latest_commit]).strip().decode('utf8')

    # Update merge message
    commit_message = ('Bump version to ' + latest_tag[1:] + '\n\n' +
                      '\n'.join(logs))
    subprocess.check_call([git, 'commit', '--amend', '-m', commit_message])

    # Set this tag to the last commit
    subprocess.check_call([git, 'tag', '-f', latest_tag])

    # Push the changes
    subprocess.check_call([git, 'push', '-f'])

    # Remove upstream tag in case it already exists
    if len(subprocess.check_output([git, 'ls-remote', 'origin', latest_tag])):
        subprocess.check_call([git, 'push', 'origin',
                               ':{0}'.format(latest_tag)])

    # Push the tag
    subprocess.check_call([git, 'push', 'origin', latest_tag])


def parse_arguments():
    parser = argparse.ArgumentParser()
    return parser.parse_args()


def main():
    args = parse_arguments()
    deploy(args)


if __name__ == '__main__':
    main()
