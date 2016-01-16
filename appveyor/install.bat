::
:: Lua
:: 
curl -fssL -o lua.zip "http://sourceforge.net/projects/luabinaries/files/5.3.2/Windows%%20Libraries/Dynamic/lua-5.3.2_Win%arch%_dllw4_lib.zip/download"
7z x lua.zip -oC:\Lua > nul
set PATH=C:\Lua;%PATH%

::
:: NSIS
::
curl -fsSL -o nsis-3.0b2-setup.exe http://prdownloads.sourceforge.net/nsis/nsis-3.0b2-setup.exe
nsis-3.0b2-setup.exe /S
set PATH=C:\Program Files (x86)\NSIS;%PATH%

::
:: UPX
::
curl -fsSL -o upx391w.zip http://upx.sourceforge.net/download/upx391w.zip
7z x upx391w.zip -oC:\UPX > nul
set PATH=C:\UPX;%PATH%

::
:: Python requirements
::

::
:: Needed by the Bintray script
::
appveyor DownloadFile https://raw.github.com/pypa/pip/master/contrib/get-pip.py
python get-pip.py
set PATH=C:\Python27\Scripts;%PATH%
pip install requests

:: Fix test86 failure introduced by python 2.7.11
:: TODO: check if this is still needed when python 2.7.12 is released.
reg copy HKLM\SOFTWARE\Python\PythonCore\2.7 HKLM\SOFTWARE\Python\PythonCore\2.7-32 /s /reg:32
reg copy HKLM\SOFTWARE\Python\PythonCore\2.7 HKLM\SOFTWARE\Python\PythonCore\2.7-32 /s /reg:64
