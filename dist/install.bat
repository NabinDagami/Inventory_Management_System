@echo off
echo Installing Inventory Beta...
echo.

REM Create application directory
if not exist "%PROGRAMFILES%\Inventory_Beta" (
    mkdir "%PROGRAMFILES%\Inventory_Beta"
)

REM Copy files
xcopy "Inventory_Beta" "%PROGRAMFILES%\Inventory_Beta\" /E /I /Q

REM Create desktop shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\shortcut.vbs"
echo sLinkFile = "%USERPROFILE%\Desktop\Inventory Beta.lnk" >> "%TEMP%\shortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\shortcut.vbs"
echo oLink.TargetPath = "%PROGRAMFILES%\Inventory_Beta\Inventory_Beta.exe" >> "%TEMP%\shortcut.vbs"
echo oLink.WorkingDirectory = "%PROGRAMFILES%\Inventory_Beta" >> "%TEMP%\shortcut.vbs"
echo oLink.IconLocation = "%PROGRAMFILES%\Inventory_Beta\_internal\assets\icons\app_icon.png" >> "%TEMP%\shortcut.vbs"
echo oLink.Description = "Inventory Beta - Inventory Management System" >> "%TEMP%\shortcut.vbs"
echo oLink.Save >> "%TEMP%\shortcut.vbs"
cscript "%TEMP%\shortcut.vbs" /nologo
del "%TEMP%\shortcut.vbs"

echo.
echo Installation complete!
echo Desktop shortcut created.
echo.
pause
