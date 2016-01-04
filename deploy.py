#!/usr/bin/env python

import argparse
import os
import subprocess
from distutils.spawn import find_executable

SCRIPT_DIR = os.path.dirname(os.path.abspath( __file__ ))


def deploy(args):
    git = find_executable('git')
    if git is None:
        raise RuntimeError('git tool not found.')

    # Move to script folder
    os.chdir(SCRIPT_DIR)

    # Switch to master branch
    subprocess.check_call([git, 'checkout', 'master'])

    # Fetch and merge upstream master branch
    subprocess.check_call([git, 'fetch', 'upstream'])
    subprocess.check_call([git, 'merge', 'upstream/master', '--no-edit'])

    # Get the latest tag
    latest_commit = subprocess.check_output([git, 'rev-list', '--tags',
                                             '--max-count=1'])
    latest_tag = subprocess.check_output([git, 'describe', '--tags',
                                          latest_commit])

    # Set this tag to the last commit
    subprocess.check_call([git, 'tag', '-f', latest_tag])

    # Push the changes
    subprocess.check_call([git, 'push'])

    # Remove upstream tag in case it already exists
    if len(subprocess.check_output([git, 'ls-remote', 'origin', latest_tag])):
      subprocess.check_call([git, 'push', 'origin',
                             ':{0}'.format( latest_tag )])

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
