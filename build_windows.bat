@echo off
REM === Windows Build Script for SOS Desktop ===
setlocal
cd /d %~dp0
echo Cleaning old build...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist sos_app.spec del sos_app.spec

echo Building EXE with PyInstaller...
pyinstaller --clean ^
  --noconfirm ^
  --name "SOS_Button_App" ^
  --add-data "_validation;_validation" ^
  --add-data "src;src" ^
  --add-data "assets;assets" ^
  --add-data "updates;updates" ^
  --icon "assets\sos_icon.ico" ^
  --specpath . ^
  sos_boot.py

echo Build complete.
echo Launch via dist\SOS_Button_App\SOS_Button_App.exe
pause
endlocal*** End Patch
