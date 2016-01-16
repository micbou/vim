::
:: Install Lua
:: 
curl -fssL -o lua.zip "http://sourceforge.net/projects/luabinaries/files/5.3.2/Windows%%20Libraries/Dynamic/lua-5.3.2_Win%arch%_dllw4_lib.zip/download"
7z x lua.zip -oC:\Lua > nul
set PATH=C:\Lua;%PATH%

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
    copy c:\gettext\libwinpthread-1.dll %APPVEYOR_BUILD_FOLDER\runtime
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
7z x upx391w.zip -oC:\UPX > nul
set PATH=C:\UPX;%PATH%

::
:: Download and install pip for Bintray script requirement.
::

appveyor DownloadFile https://raw.github.com/pypa/pip/master/contrib/get-pip.py
python get-pip.py
set PATH=C:\Python27\Scripts;%PATH%
pip install requests

:: Fix test86 failure introduced by python 2.7.11
:: TODO: check if this is still needed when python 2.7.12 is released.
reg copy HKLM\SOFTWARE\Python\PythonCore\2.7 HKLM\SOFTWARE\Python\PythonCore\2.7-32 /s /reg:32
reg copy HKLM\SOFTWARE\Python\PythonCore\2.7 HKLM\SOFTWARE\Python\PythonCore\2.7-32 /s /reg:64
