rem Set environment variables.
rem   @param arch Architecture (32 or 64)
rem   @param msvc Microsoft Visual C++ version
rem   @param appveyor_repo_tag_name AppVeyor tag (Vim tags are in vX.Y.Z form)

setlocal

if %arch% == 32 (
    set vim_arch=x86
) else (
    set vim_arch=x64
)

:: Get major.minor version from full version
for /F "tokens=1,2 delims=." %%a in ("%lua_version%") do (
   set lua_major_minor_version=%%a.%%b
)
for /F "tokens=1,2 delims=." %%a in ("%perl_version%") do (
   set perl_major_minor_version=%%a.%%b
)
for /F "tokens=1,2 delims=." %%a in ("%python2_version%") do (
   set python2_major_minor_version=%%a.%%b
)
for /F "tokens=1,2 delims=." %%a in ("%python3_version%") do (
   set python3_major_minor_version=%%a.%%b
)
for /F "tokens=1,2 delims=." %%a in ("%racket_version%") do (
   set racket_major_minor_version=%%a.%%b
)
for /F "tokens=1,2 delims=." %%a in ("%ruby_version%") do (
   set ruby_major_minor_version=%%a.%%b
)
for /F "tokens=1,2 delims=." %%a in ("%tcl_version%") do (
   set tcl_major_minor_version=%%a.%%b
)

endlocal & (
    set vim_version=%appveyor_repo_tag_name:~1%
    set vim_artifact=vim%vim_version%-%vim_arch%.exe
    set vim_description=Vim %vim_version% 32-bit and 64-bit for Windows with Lua %lua_major_minor_version%, Perl %perl_major_minor_version%, Python %python2_major_minor_version%, Python %python3_major_minor_version%, Racket %racket_major_minor_version%, Ruby %ruby_major_minor_version%, and Tcl %tcl_major_minor_version% support. Compiled with MSVC %msvc%.
)

echo %vim_description%
