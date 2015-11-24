#!/usr/bin/env python

import argparse
import os
import shutil
import subprocess
from distutils.spawn import find_executable

SCRIPT_DIR = os.path.dirname(os.path.abspath( __file__ ))
SOURCES_DIR = os.path.join(SCRIPT_DIR, 'src')
RUNTIME_DIR = os.path.join(SCRIPT_DIR, 'runtime')
DOC_DIR = os.path.join(RUNTIME_DIR, 'doc')
XXD_DIR = os.path.join(SOURCES_DIR, 'xxd')
GVIM_EXT_DIR = os.path.join(SOURCES_DIR, 'GvimExt')
GVIM_NSIS_PATH = os.path.join(SCRIPT_DIR, 'nsis', 'gvim.nsi')


def generate_uganda_file():
    shutil.copy(os.path.join(DOC_DIR, 'uganda.txt'),
                os.path.join(DOC_DIR, 'uganda.nsis.txt'))


def install_vim(args):
    generate_uganda_file()

    shutil.copy(os.path.join(SOURCES_DIR, 'install.exe'),
                os.path.join(SOURCES_DIR, 'installw32.exe'))

    shutil.copy(os.path.join(SOURCES_DIR, 'uninstal.exe'),
                os.path.join(SOURCES_DIR, 'uninstalw32.exe'))

    shutil.copy(os.path.join(SOURCES_DIR, 'gvim.exe'),
                os.path.join(SOURCES_DIR, 'gvim_ole.exe'))

    shutil.copy(os.path.join(SOURCES_DIR, 'xxd', 'xxd.exe'),
                os.path.join(SOURCES_DIR, 'xxdw32.exe'))

    shutil.copy(os.path.join(SOURCES_DIR, 'vim.exe'),
                os.path.join(SOURCES_DIR, 'vimw32.exe'))

    shutil.copy(os.path.join(GVIM_EXT_DIR, 'gvimext.dll'),
                os.path.join(GVIM_EXT_DIR, 'gvimext64.dll'))

    upx = find_executable('upx')
    if upx is None:
        print('WARNING: Ultimate Packer eXecutables is not available.')

    makensis = find_executable('makensis')
    if makensis is None:
        raise RuntimeError('Cannot find makensis executable. '
                           'Did you install NSIS?')

    subprocess.check_call([makensis, GVIM_NSIS_PATH])


def parse_arguments():
    parser = argparse.ArgumentParser()
    return parser.parse_args()


def main():
    args = parse_arguments()
    install_vim(args)


if __name__ == '__main__':
    main()
