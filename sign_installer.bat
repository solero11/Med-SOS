@echo off
set SIGNTOOL="C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe"
set CERT_PATH=certs\sos_button_cert.pfx
set TIMESTAMP_URL=http://timestamp.digicert.com
set PASSWORD=your_password_here
%SIGNTOOL% sign /f "%CERT_PATH%" /p %PASSWORD% /tr %TIMESTAMP_URL% /td SHA256 /fd SHA256 dist\installer\SOS_Button_Installer.exe
