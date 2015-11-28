rem Set environment variables.
rem   @param arch Architecture (32 or 64)
rem   @param msvc Microsoft Visual C++ version
rem   @param appveyor_repo_tag_name AppVeyor tag (Vim tags are in vX.Y.Z form)

if %arch% == 32 (
    set vim_arch=x86
) else (
    set vim_arch=x64
)

set vim_version=%appveyor_repo_tag_name:~1%
set vim_artifact=vim%vim_version%-%vim_arch%.exe
set vim_description=Vim %vim_version% 32-bit and 64-bit for Windows with python 2.7 and python 3.4 support. Compiled with MSVC %msvc%.
