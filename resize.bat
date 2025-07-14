
@echo off
REM Zjistí aktuální adresář, odkud je skript volán
set "CALLDIR=%CD%"

REM Pokud není zadán argument, použije 50 %
set "PERCENT=%~1"
if "%PERCENT%"=="" set "PERCENT=50"

REM Cesta ke skriptu (uprav dle potřeby, pokud není v PATH)
REM Předpokládáme, že pok.py je ve stejné složce jako tento .bat
set "SCRIPT=%~dp0resize.py"

REM Spustí Python s předáním cesty a procenta
"c:\Users\herzog\AppData\Local\Programs\GIMP 3\bin\python.exe" "%SCRIPT%" "%CALLDIR%" %PERCENT%
