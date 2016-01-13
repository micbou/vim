#!/usr/bin/env python

import argparse
import os
import subprocess
import platform
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath( __file__ ))
ROOT_DIR = os.path.join(SCRIPT_DIR, '..')
SOURCES_DIR = os.path.join(ROOT_DIR, 'src')

MAKE_PATH = os.path.join(SOURCES_DIR, 'Make_mvc.mak')
APPVEYOR_MAKE_PATH = os.path.join(SOURCES_DIR, 'Make_mvc_appveyor.mak')

MSVC_BIN_DIR = os.path.join('..', '..', 'VC', 'bin')
VC_VARS_SCRIPT = os.path.join('..', '..', 'VC', 'vcvarsall.bat')

SDK_INCLUDE_DIR = ( r'C:\Program Files (x86)\Microsoft SDKs\Windows'
                    r'\v7.1A\Include' )


def get_arch_build_args(args):
    if args.arch == 64:
        return 'CPU=AMD64'
    return 'CPU=i386'


def get_python2_path(args):
    if args.python2:
        return args.python2
    if args.arch == 64:
        return r'C:\Python27-x64'
    return r'C:\Python27'


def get_python3_path(args):
    if args.python3:
        return args.python3
    if args.arch == 64:
        return r'C:\Python34-x64'
    return r'C:\Python34'


def get_pythons_build_args(args):
    python2_path = get_python2_path(args)
    python3_path = get_python3_path(args)

    return ['PYTHON_VER=27',
            'DYNAMIC_PYTHON=yes',
            'PYTHON={0}'.format(python2_path),
            'PYTHON3_VER=34',
            'DYNAMIC_PYTHON3=yes',
            'PYTHON3={0}'.format(python3_path)]


def get_msvc_dir(args):
    if args.msvc == 11:
        return os.path.join(os.environ['VS110COMNTOOLS'], MSVC_BIN_DIR)
    if args.msvc == 12:
        return os.path.join(os.environ['VS120COMNTOOLS'], MSVC_BIN_DIR)
    if args.msvc == 14:
        return os.path.join(os.environ['VS140COMNTOOLS'], MSVC_BIN_DIR)
    raise RuntimeError('msvc parameter should be 11, 12, or 14.')


def get_vc_mod(arch):
    if arch == 64:
        return 'x86_amd64'
    return 'x86'


def get_build_args(args, gui=True):
    build_args = [get_arch_build_args(args)]

    if gui:
        build_args.extend(['GUI=yes',
                           'OLE=yes',
                           'IME=yes',
                           'GIME=yes',
                           'DIRECTX=yes'])
        # MSVC 14 will fail to build gvim with XPM image support enabled.
        # See https://groups.google.com/forum/#!topic/vim_dev/6DfnCX9TjYI
        if args.msvc == 14:
            build_args.append('XPM=no')

    build_args.extend(['WINVER=0x0500',
                       'FEATURES=HUGE',
                       'MBYTE=yes',
                       'ICONV=yes',
                       'DEBUG=no'])

    if args.credit:
        build_args.extend(['USERNAME={0}'.format(args.credit),
                           'USERDOMAIN='])

    build_args.extend(get_pythons_build_args(args))

    return build_args


def build_vim(args, gui = True):
    os.chdir(SOURCES_DIR)

    new_env = os.environ.copy()

    if not os.path.exists(SDK_INCLUDE_DIR):
        raise RuntimeError('SDK include folder does not exist.')

    new_env['SDK_INCLUDE_DIR'] = SDK_INCLUDE_DIR

    msvc_dir = get_msvc_dir(args)

    nmake = os.path.join(msvc_dir, 'nmake.exe')
    if not os.path.exists(nmake):
        raise RuntimeError('nmake tool not found.')

    build_args = get_build_args(args, gui)

    vc_vars_script_path = os.path.join(msvc_dir, VC_VARS_SCRIPT)
    vc_vars_cmd = [vc_vars_script_path, get_vc_mod(args.arch)]

    clean_cmd = vc_vars_cmd
    clean_cmd.extend(['&', nmake, '/f', APPVEYOR_MAKE_PATH, 'clean'])
    clean_cmd.extend(build_args)

    subprocess.check_call(clean_cmd, env = new_env)

    build_cmd = vc_vars_cmd
    build_cmd.extend(['&', nmake, '/f', APPVEYOR_MAKE_PATH])
    build_cmd.extend(build_args)

    subprocess.check_call(build_cmd, env = new_env)


def get_arch_from_python_interpreter():
    if platform.architecture()[0] == '64bit':
        return 64
    return 32


def remove_progress_bars():
    # Progress bars from the build are messing up the logs on AppVeyor.
    # Create a new make file that remove them.
    with open(MAKE_PATH, "r") as make_file:
        lines = make_file.readlines()
    with open(APPVEYOR_MAKE_PATH, "w") as appveyor_make_file:
        for line in lines:
            appveyor_make_file.write(re.sub(r'\$\(LINKARGS2\)',
                                            r'$(LINKARGS2) | '
                                            r"sed -e 's#.*\\r.*##'",
                                            line))


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--msvc', type = int, choices = [11, 12, 14],
                        default = 12, help = 'choose the Microsoft Visual '
                        'Studio version (default: %(default)s).' )
    parser.add_argument('--arch', type = int, choices = [32, 64],
                        help = 'force architecture to 32 or 64 bits on '
                        'Windows (default: python interpreter architecture).' )
    parser.add_argument('--python2', type = str,
                        help = 'set python2 folder (default: C:\Python27 or '
                        'C:\Python27-x64 depending on architecture)')
    parser.add_argument('--python3', type = str,
                        help = 'set python3 folder (default: C:\Python34 or '
                        'C:\Python34-x64 depending on architecture)')
    parser.add_argument('--credit', type = str,
                        help = 'replace username@userdomain by a custom '
                               'string in compilation credit.')

    args = parser.parse_args()
    if not args.arch:
        args.arch = get_arch_from_python_interpreter()

    return args


def main():
    args = parse_arguments()
    remove_progress_bars()
    build_vim(args, gui = False)
    build_vim(args)


if __name__ == '__main__':
    main()
