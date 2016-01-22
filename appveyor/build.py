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

VERSION_REGEX = re.compile('([0-9]+).([0-9]+)(.([0-9]+)){0,2}')


def get_major_minor_version(version):
    matches = VERSION_REGEX.match(version)
    if not matches:
        raise RuntimeError('Wrong version format: {0}'.format(version))
    return matches.group(1) + '.' + matches.group(2)


def get_minimal_version(version):
    matches = VERSION_REGEX.match(version)
    if not matches:
        raise RuntimeError('Wrong version format: {0}'.format(version))
    return matches.group(1) + matches.group(2)


def get_arch_build_args(args):
    if args.arch == 64:
        return 'CPU=AMD64'
    return 'CPU=i386'


def get_lua_build_args(args):
    lua_version = get_minimal_version(args.lua_version)

    return ['LUA={0}'.format(args.lua_path),
            'LUA_VER={0}'.format(lua_version),
            'DYNAMIC_LUA=yes']


def get_perl_path(args):
    if args.perl_path:
        return args.perl_path

    perl_version = get_minimal_version(args.perl_version)

    return r'C:\Perl{0}\perl'.format(perl_version)


def get_perl_build_args(args):
    perl_path = get_perl_path(args)
    perl_version = get_minimal_version(args.perl_version)

    return ['PERL={0}'.format(perl_path),
            'PERL_VER={0}'.format(perl_version),
            'DYNAMIC_PERL=yes']


def get_python2_path(args):
    if args.python2_path:
        return args.python2_path

    python2_version = get_minimal_version(args.python2_version)

    if args.arch == 64:
        return r'C:\Python{0}-x64'.format(python2_version)
    return r'C:\Python{0}'.format(python2_version)


def get_python3_path(args):
    if args.python3_path:
        return args.python3_path

    python3_version = get_minimal_version(args.python3_version)

    if args.arch == 64:
        return r'C:\Python{0}-x64'.format(python3_version)
    return r'C:\Python{0}'.format(python3_version)


def get_pythons_build_args(args):
    python2_path = get_python2_path(args)
    python3_path = get_python3_path(args)

    python2_version = get_minimal_version(args.python2_version)
    python3_version = get_minimal_version(args.python3_version)

    return ['PYTHON_VER={0}'.format(python2_version),
            'DYNAMIC_PYTHON=yes',
            'PYTHON={0}'.format(python2_path),
            'PYTHON3_VER={0}'.format(python3_version),
            'DYNAMIC_PYTHON3=yes',
            'PYTHON3={0}'.format(python3_path)]


def get_racket_build_args(args):
    return ['MZSCHEME={0}'.format(args.racket_path),
            'MZSCHEME_VER={0}'.format(args.racket_library),
            'DYNAMIC_MZSCHEME=yes']


def get_ruby_path(args):
    if args.ruby_path:
        return args.ruby_path

    ruby_version = get_minimal_version(args.ruby_version)

    if args.arch == 64:
        return r'C:\Ruby{0}-x64'.format(ruby_version)
    return r'C:\Ruby{0}'.format(ruby_version)


def get_ruby_build_args(args):
    ruby_path = get_ruby_path(args)
    ruby_ver_long = args.ruby_version
    ruby_ver = get_minimal_version(args.ruby_version)

    return ['RUBY={0}'.format(ruby_path),
            'RUBY_VER_LONG={0}'.format(ruby_ver_long),
            'RUBY_VER={0}'.format(ruby_ver),
            'DYNAMIC_RUBY=yes',
            'RUBY_MSVCRT_NAME=msvcrt']


def get_tcl_build_args(args):
    tcl_ver_long = get_major_minor_version(args.tcl_version)
    tcl_ver = get_minimal_version(args.tcl_version)

    return ['TCL={0}'.format(args.tcl_path),
            'TCL_VER_LONG={0}'.format(tcl_ver_long),
            'TCL_VER={0}'.format(tcl_ver),
            'DYNAMIC_TCL=yes']


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
        # TODO: find a way to fix this.
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

    build_args.extend(get_lua_build_args(args))
    build_args.extend(get_perl_build_args(args))
    build_args.extend(get_pythons_build_args(args))
    build_args.extend(get_racket_build_args(args))
    build_args.extend(get_ruby_build_args(args))
    build_args.extend(get_tcl_build_args(args))

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


def clean_up():
    if os.path.isfile(APPVEYOR_MAKE_PATH):
        os.remove(APPVEYOR_MAKE_PATH)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--msvc', type = int, choices = [11, 12, 14],
                        default = 12, help = 'choose the Microsoft Visual '
                        'Studio version (default: %(default)s).' )
    parser.add_argument('--arch', type = int, choices = [32, 64],
                        help = 'force architecture to 32 or 64 bits on '
                        'Windows (default: python interpreter architecture).' )
    parser.add_argument('--lua-path', type = str, default = 'C:\Lua',
                        help = 'set Lua folder (default: C:\Lua)')
    parser.add_argument('--lua-version', type = str, default = '5.3',
                        help = 'set Lua version (default: 5.3)')
    parser.add_argument('--perl-path', type = str,
                        help = 'set Perl folder (default: C:\Perl{ver})')
    parser.add_argument('--perl-version', type = str, default = '5.22.1.2201',
                        help = 'set Perl version (default: 5.22.1.2201)')
    parser.add_argument('--python2-path', type = str,
                        help = 'set Python2 folder (default: C:\Python{ver} '
                        'or C:\Python{ver}-x64 depending on architecture)')
    parser.add_argument('--python2-version', type = str, default = '2.7',
                        help = 'set Python2 version (default: 2.7)')
    parser.add_argument('--python3-path', type = str,
                        help = 'set Python3 folder (default: C:\Python{ver} '
                        'or C:\Python{ver}-x64 depending on architecture)')
    parser.add_argument('--python3-version', type = str, default = '3.4',
                        help = 'set Python3 version (default: 3.4)')
    parser.add_argument('--racket-path', type = str, default = 'C:\Racket',
                        help = 'set Racket folder (default: C:\Racket)')
    parser.add_argument('--racket-library', type = str, default = '3m_9z0ds0',
                        help = 'set Racket library version name '
                               '(default: 3m_9z0ds0)')
    parser.add_argument('--ruby-path', type = str,
                        help = 'set Ruby folder (default: C:\Ruby{ver})')
    parser.add_argument('--ruby-version', type = str, default = '2.2.0',
                        help = 'set Ruby version (default: 2.2.0)')
    parser.add_argument('--tcl-path', type = str, default = 'C:\Tcl',
                        help = 'set Tcl folder (default: C:\Tcl)')
    parser.add_argument('--tcl-version', type = str, default = '8.6.4.1',
                        help = 'set Tcl version (default: 8.6.4.1)')
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
    clean_up()


if __name__ == '__main__':
    main()
