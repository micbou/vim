rem Set an environement variable containing the artifact name.

if %1 == 32 (
    set arch=x86
) else (
    set arch=x64
)

set tag=%2
set version=%tag:~1%

set artifact=vim%version%-%arch%.exe
