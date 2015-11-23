#!/usr/bin/env python

import argparse
import requests
import os

BINTRAY_URL = ( 'https://api.bintray.com/content/'
                '{subject}/'
                '{repo}/'
                '{package}/'
                '{version}/'
                '{file_path}' )


def upload_to_bintray(args):
    params = {
        'publish': 1 if args.publish else 0,
        'override': 1 if args.override else 0,
        'explode': 1 if args.explode else 0
    }

    url = BINTRAY_URL.format(subject = args.subject,
                             repo = args.repo,
                             package = args.package,
                             version = args.version,
                             file_path = args.filepath)

    with open(args.file_input, 'rb') as f:
        response = requests.put(url,
                                data = f,
                                params = params,
                                auth = (args.username,
                                        args.api_key))

    if response.status_code != 201:
        print('Bintray upload failed with message: {0}'
              .format(response.text))


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('subject', type = str,
                        help = 'Bintray account.')
    parser.add_argument('repo', type = str,
                        help = 'Bintray repository.')
    parser.add_argument('package', type = str,
                        help = 'Bintray package.')
    parser.add_argument('version', type = str,
                        help = 'Bintray version.')
    parser.add_argument('file_input', type = str,
                        help = 'File to upload.')
    parser.add_argument('username', type = str,
                        help = 'Bintray username.')
    parser.add_argument('api_key', type = str,
                        help = 'Bintray API key.')
    parser.add_argument('--filepath', type = str,
                        help = 'Bintray file path (default: file input '
                               'basename).')
    parser.add_argument('--publish', action='store_true',
                        help = 'Publish the uploaded artifact as part of '
                               'uploading.')
    parser.add_argument('--override', action='store_true',
                        help = 'Overwrite already published artifact.')
    parser.add_argument('--explode', action='store_true',
                        help = 'Unknown behavior.')

    args = parser.parse_args()

    args.filepath = ( args.filepath if args.filepath else
                      os.path.basename(args.file_input) )

    return args


def main():
    args = parse_arguments()
    upload_to_bintray(args)


if __name__ == '__main__':
    main()
