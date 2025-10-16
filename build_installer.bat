@echo off
cd /d %~dp0
echo === Building Installer ===
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" build_installer.iss
echo Installer created under dist\installer\
pause
