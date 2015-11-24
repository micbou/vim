#!/usr/bin/env python

import argparse
import os
import shutil
import subprocess
from distutils.spawn import find_executable

SCRIPT_DIR = os.path.dirname(os.path.abspath( __file__ ))
SOURCES_DIR = os.path.join(SCRIPT_DIR, 'src')
RUNTIME_DIR = os.path.join(SCRIPT_DIR, 'runtime')
NSIS_DIR = os.path.join(SCRIPT_DIR, 'nsis')
DOC_DIR = os.path.join(RUNTIME_DIR, 'doc')
XXD_DIR = os.path.join(SOURCES_DIR, 'xxd')
GVIM_EXT_DIR = os.path.join(SOURCES_DIR, 'GvimExt')
GVIM_NSIS_PATH = os.path.join(NSIS_DIR, 'gvim.nsi')
GVIM_INSTALLER_PATH = os.path.join(NSIS_DIR, 'gvim-installer.exe')


def generate_uganda_file():
    shutil.copy(os.path.join(DOC_DIR, 'uganda.txt'),
                os.path.join(DOC_DIR, 'uganda.nsis.txt'))


def rename_vim_installer(args):
    arch_name = ('x64' if args.arch == 64 else
                 'x86')
    installer_name = 'vim{0}-{1}'.format(args.tag, arch_name)

    shutil.move(GVIM_INSTALLER_PATH,
                os.path.join(GVIM_NSIS_PATH, installer_name))


def generate_vim_installer(args):
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

    rename_vim_installer(args)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('arch', type = int, choices = [32, 64],
                        help = 'Architecture used to build Vim '
                               '(32 or 64 bits).')
    parser.add_argument('tag', type = str,
                        help = 'Tag for current build.')

    args = parser.parse_args()

    return args


def main():
    args = parse_arguments()
    generate_vim_installer(args)


if __name__ == '__main__':
    main()
