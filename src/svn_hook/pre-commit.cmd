@ECHO OFF
:: Set parameters. 

set REPOS=%1
set TXN=%2

:: Execute python script for pre-check-in verification
C:\PythonEnv\Scripts\python.exe E:\Repositories\Gateway\hooks\svn-ci.py -p %REPOS% -t %TXN%