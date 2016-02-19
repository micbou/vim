" This script is sourced while editing the .vim file with the tests.
" When the script is successful the .res file will be created.
" Errors are appended to the test.log file.
"
" The test script may contain anything, only functions that start with
" "Test_" are special.  These will be invoked and should contain assert
" functions.  See test_assert.vim for an example.
"
" It is possible to source other files that contain "Test_" functions.  This
" can speed up testing, since Vim does not need to restart.  But be careful
" that the tests do not interfere with each other.
"
" If an error cannot be detected properly with an assert function add the
" error to the v:errors list:
"   call add(v:errors, 'test foo failed: Cannot find xyz')
"
" If preparation for each Test_ function is needed, define a SetUp function.
" It will be called before each Test_ function.
"
" If cleanup after each Test_ function is needed, define a TearDown function.
" It will be called after each Test_ function.
"
" When debugging a test it can be useful to add messages to v:errors:
" 	call add(v:errors, "this happened")


" Without the +eval feature we can't run these tests, bail out.
so small.vim

" Check that the screen size is at least 24 x 80 characters.
if &lines < 24 || &columns < 80 
  let error = 'Screen size too small! Tests require at least 24 lines with 80 characters'
  echoerr error
  split test.log
  $put =error
  w
  cquit
endif

" For consistency run all tests with 'nocompatible' set.
" This also enables use of line continuation.
set nocp viminfo+=nviminfo

" Avoid stopping at the "hit enter" prompt
set nomore

" Output all messages in English.
lang mess C

" Always use forward slashes.
set shellslash

let s:srcdir = expand('%:p:h:h')

" Support function: get the alloc ID by name.
function GetAllocId(name)
  exe 'split ' . s:srcdir . '/alloc.h'
  let top = search('typedef enum')
  if top == 0
    call add(v:errors, 'typedef not found in alloc.h')
  endif
  let lnum = search('aid_' . a:name . ',')
  if lnum == 0
    call add(v:errors, 'Alloc ID ' . a:name . ' not defined')
  endif
  close
  return lnum - top - 1
endfunc


" Source the test script.  First grab the file name, in case the script
" navigates away.  g:testname can be used by the tests.
let g:testname = expand('%')
let s:done = 0
let s:fail = 0
let s:errors = []
let s:messages = []
if expand('%') =~ 'test_viml.vim'
  " this test has intentional s:errors, don't use try/catch.
  source %
else
  try
    source %
  catch
    let s:fail += 1
    call add(s:errors, 'Caught exception: ' . v:exception . ' @ ' . v:throwpoint)
  endtry
endif

" Locate Test_ functions and execute them.
set nomore
redir @q
silent function /^Test_
redir END
let s:tests = split(substitute(@q, 'function \(\k*()\)', '\1', 'g'))

" Execute the tests in alphabetical order.
for s:test in sort(s:tests)
  echo 'Executing ' . s:test
  if exists("*SetUp")
    call SetUp()
  endif

  call add(s:messages, 'Executing ' . s:test)
  let s:done += 1
  try
    exe 'call ' . s:test
  catch
    call add(v:errors, 'Caught exception in ' . s:test . ': ' . v:exception . ' @ ' . v:throwpoint)
  endtry

  if len(v:errors) > 0
    let s:fail += 1
    call add(s:errors, 'Found errors in ' . s:test . ':')
    call extend(s:errors, v:errors)
    let v:errors = []
  endif

  if exists("*TearDown")
    call TearDown()
  endif
endfor

if s:fail == 0
  " Success, create the .res file so that make knows it's done.
  exe 'split ' . fnamemodify(g:testname, ':r') . '.res'
  write
endif

if len(s:errors) > 0
  " Append errors to test.log
  split test.log
  call append(line('$'), '')
  call append(line('$'), 'From ' . g:testname . ':')
  call append(line('$'), s:errors)
  write
endif

let message = 'Executed ' . s:done . (s:done > 1 ? ' tests' : ' test')
echo message
call add(s:messages, message)
if s:fail > 0
  let message = s:fail . ' FAILED:'
  echo message
  call add(s:messages, message)
  call extend(s:messages, s:errors)
endif

" Append messages to "messages"
split messages
call append(line('$'), '')
call append(line('$'), 'From ' . g:testname . ':')
call append(line('$'), s:messages)
write

qall!
