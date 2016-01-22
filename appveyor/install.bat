::
:: Install Lua
::
curl -fssL -o lua.zip "http://sourceforge.net/projects/luabinaries/files/5.3.2/Windows%%20Libraries/Dynamic/lua-5.3.2_Win%arch%_dllw4_lib.zip/download"
7z x lua.zip -oC:\Lua > nul
set PATH=C:\Lua;%PATH%

::
:: Install Perl
::

:: Use local environment variables to avoid conflicts with variables in Vim makefile.
setlocal

if %arch% == 32 (
    set perl_arch=x86-64int
) else (
    set perl_arch=x64
)
set perl_folder=ActivePerl-%perl_version%-MSWin32-%perl_arch%-%perl_revision%

appveyor DownloadFile http://downloads.activestate.com/ActivePerl/releases/%perl_version%/%perl_folder%.zip
7z x %perl_folder%.zip -oC:\ > nul

:: Deduce minimal version format from full version (ex: 5.22.1.2201 gives 522).
for /F "tokens=1,2 delims=." %%a in ("%perl_version%") do (
   set perl_minimal_version=%%a%%b
)
move C:\%perl_folder% C:\Perl%perl_minimal_version%

endlocal & set PATH=C:\Perl%perl_minimal_version%\perl\bin;%PATH%

::
:: Install Ruby
::
setlocal

:: RubyInstaller is built by MinGW, so we cannot use header files from it.
:: Download the source files and generate config.h for MSVC.

:: Get the branch according to Ruby version
for /F "tokens=1,2 delims=." %%a in ("%ruby_version%") do (
   set ruby_branch=ruby_%%a_%%b
   set ruby_minimal_version=%%a%%b
)

git clone https://github.com/ruby/ruby.git -b %ruby_branch% --depth 1 -q %APPVEYOR_BUILD_FOLDER%\ruby
pushd %APPVEYOR_BUILD_FOLDER%\ruby

if %msvc% == 11 (
    set vc_vars_script_path="%VS110COMNTOOLS%\..\..\VC\vcvarsall.bat"
)
if %msvc% == 12 (
    set vc_vars_script_path="%VS120COMNTOOLS%\..\..\VC\vcvarsall.bat"
)
if %msvc% == 14 (
    set vc_vars_script_path="%VS140COMNTOOLS%\..\..\VC\vcvarsall.bat"
)

if %arch% == 32 (
    call %vc_vars_script_path% x86
) else (
    call %vc_vars_script_path% x86_amd64
)

call win32\configure.bat
nmake .config.h.time

if %arch% == 32 (
    set ruby_path=C:\Ruby%ruby_minimal_version%
) else (
    set ruby_path=C:\Ruby%ruby_minimal_version%-x64
)

xcopy /s .ext\include %ruby_path%\include\ruby-%ruby_version%
popd

endlocal & set PATH=%ruby_path%\bin;%PATH%

::
:: Get diff.exe from old gvim binaries.
::
curl -fssL -O ftp://ftp.vim.org/pub/vim/pc/gvim74.exe
7z e gvim74.exe $0\diff.exe -o..

::
:: Get libintl.dll, iconv.dll, and possibly libwinpthread.dll.
::
curl -fssL "https://github.com/mlocati/gettext-iconv-windows/releases/download/v0.19.6-v1.14/gettext0.19.6-iconv1.14-shared-64.exe" -o gettext.exe
start /wait gettext.exe /verysilent /dir=c:\gettext
copy c:\gettext\libintl-8.dll %APPVEYOR_BUILD_FOLDER%\runtime
copy c:\gettext\libiconv-2.dll %APPVEYOR_BUILD_FOLDER%\runtime
:: Copy libwinpthread only for 64-bits
if %arch% == 64 (
    copy c:\gettext\libwinpthread-1.dll %APPVEYOR_BUILD_FOLDER%\runtime
)

::
:: Install NSIS.
::
curl -fsSL -o nsis-3.0b2-setup.exe http://prdownloads.sourceforge.net/nsis/nsis-3.0b2-setup.exe
nsis-3.0b2-setup.exe /S
set PATH=C:\Program Files (x86)\NSIS;%PATH%

::
:: Install UPX.
::
curl -fsSL -o upx391w.zip http://upx.sourceforge.net/download/upx391w.zip
7z x upx391w.zip -oC:\ > nul
set PATH=C:\upx391w;%PATH%

::
:: Download and install pip for Bintray script requirement.
::

appveyor DownloadFile https://bootstrap.pypa.io/get-pip.py
python get-pip.py
set PATH=C:\Python27\Scripts;%PATH%
pip install requests

:: Fix test86 failure introduced by python 2.7.11
:: TODO: check if this is still needed when python 2.7.12 is released.
reg copy HKLM\SOFTWARE\Python\PythonCore\2.7 HKLM\SOFTWARE\Python\PythonCore\2.7-32 /s /reg:32
reg copy HKLM\SOFTWARE\Python\PythonCore\2.7 HKLM\SOFTWARE\Python\PythonCore\2.7-32 /s /reg:64
