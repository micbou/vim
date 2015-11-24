#!/usr/bin/env python

import argparse
import os
import subprocess
import platform

SCRIPT_DIR = os.path.dirname(os.path.abspath( __file__ ))
SOURCES_DIR = os.path.join(SCRIPT_DIR, 'src')

MSVC11_ROOT_DIR = r'C:\Program Files (x86)\Microsoft Visual Studio 11.0'
MSVC12_ROOT_DIR = r'C:\Program Files (x86)\Microsoft Visual Studio 12.0'
MSVC14_ROOT_DIR = r'C:\Program Files (x86)\Microsoft Visual Studio 14.0'

MSVC_BIN_DIR = os.path.join('VC', 'bin')
VC_VARS_32_SCRIPT = 'vcvars32.bat'
VC_VARS_64_SCRIPT = os.path.join('x86_amd64', 'vcvarsx86_amd64.bat')

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


def get_vc_vars_script_path(arch, msvc_dir):
    if arch == 64:
        return os.path.join(msvc_dir, VC_VARS_64_SCRIPT)
    return os.path.join(msvc_dir, VC_VARS_32_SCRIPT)


def build_vim(args, gui = True):
    os.chdir(SOURCES_DIR)

    msvc_dir = get_msvc_dir(args)

    vc_vars_script_path = get_vc_vars_script_path(args.arch, msvc_dir)
    build_cmd = [vc_vars_script_path]

    new_env = os.environ.copy()

    if not os.path.exists(SDK_INCLUDE_DIR):
        raise RuntimeError('SDK include folder does not exist.')

    new_env['SDK_INCLUDE_DIR'] = SDK_INCLUDE_DIR

    nmake = os.path.join(msvc_dir, 'nmake.exe')
    if not os.path.exists(nmake):
        raise RuntimeError('nmake tool not found.')

    build_cmd.extend(['&',
                      nmake, '-f',
                      'Make_mvc.mak'])

    build_cmd.append(get_arch_build_args(args))

    if gui:
        build_cmd.extend(['GUI=yes',
                          'IME=yes'])

    build_cmd.extend(['MBYTE=yes',
                      'ICONV=yes',
                      'DEBUG=no'])

    build_cmd.extend(get_pythons_build_args(args))

    subprocess.check_call(build_cmd, env = new_env)


def get_arch_from_python_interpreter():
    if platform.architecture()[0] == '64bit':
        return 64
    return 32


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--msvc', type = int, choices = [11, 12, 14],
                        default = 12, help = 'Choose the Microsoft Visual '
                        'Studio version (default: %(default)s).' )
    parser.add_argument('--arch', type = int, choices = [32, 64],
                        help = 'Force architecture to 32 or 64 bits on '
                        'Windows (default: python interpreter architecture).' )
    parser.add_argument('--python2', type = str,
                        help = 'Set python2 folder (default: C:\Python27 or '
                        'C:\Python27-64 depending on architecture)')
    parser.add_argument('--python3', type = str,
                        help = 'Set python3 folder (default: C:\Python35 or '
                        'C:\Python35-64 depending on architecture)')

    args = parser.parse_args()
    if not args.arch:
        args.arch = get_arch_from_python_interpreter()

    return args


def main():
    args = parse_arguments()
    build_vim(args, gui = False)
    build_vim(args)


if __name__ == '__main__':
    main()
