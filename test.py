#!/usr/bin/env python

import argparse
import os
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath( __file__ ))
SOURCES_DIR = os.path.join(SCRIPT_DIR, 'src')
TESTS_DIR = os.path.join(SOURCES_DIR, 'testdir')

MSVC11_ROOT_DIR = r'C:\Program Files (x86)\Microsoft Visual Studio 11.0'
MSVC12_ROOT_DIR = r'C:\Program Files (x86)\Microsoft Visual Studio 12.0'
MSVC14_ROOT_DIR = r'C:\Program Files (x86)\Microsoft Visual Studio 14.0'

MSVC_BIN_DIR = os.path.join('VC', 'bin')


def get_msvc_dir(args):
    if args.msvc == 11:
        msvc_dir = os.path.join(MSVC11_ROOT_DIR, MSVC_BIN_DIR)
    if args.msvc == 12:
        msvc_dir = os.path.join(MSVC12_ROOT_DIR, MSVC_BIN_DIR)
    if args.msvc == 14:
        msvc_dir = os.path.join(MSVC14_ROOT_DIR, MSVC_BIN_DIR)
    if not os.path.exists(msvc_dir):
        raise RuntimeError('{0} folder does not exist. Did you install '
                           'Microsoft Visual C++ {1}?'.format(msvc_dir,
                                                              args.msvc))
    return msvc_dir


def test_vim(args):
    os.chdir(TESTS_DIR)

    msvc_dir = get_msvc_dir(args)

    nmake = os.path.join(msvc_dir, 'nmake.exe')
    if not os.path.exists(nmake):
        raise RuntimeError('nmake tool not found.')

    gvim_path = os.path.join(SOURCES_DIR, 'gvim')

    test_cmd = [nmake, '-f',
                'Make_dos.mak',
                'VIMPROG={0}'.format(gvim_path)]

    subprocess.check_call(test_cmd)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--msvc', type = int, choices = [11, 12, 14],
                        default = 12, help = 'Choose the Microsoft Visual '
                        'Studio version (default: %(default)s).' )

    return parser.parse_args()


def main():
    args = parse_arguments()
    test_vim(args)


if __name__ == '__main__':
    main()
