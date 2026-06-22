@echo off
title Inventory Beta - Installer
echo ============================================
echo    Inventory Beta - Installer
echo ============================================
echo.

:: Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Please run this file as Administrator.
    echo Right-click install.bat ^> "Run as administrator"
    pause
    exit /b 1
)

:: Set install path
set "INSTALL_DIR=%PROGRAMFILES%\Inventory Beta"
set "EXE_SOURCE=%~dp0dist\Inventory_Beta\Inventory_Beta.exe"
set "INTERNAL_SOURCE=%~dp0dist\Inventory_Beta\_internal"

:: Check if build exists
if not exist "%EXE_SOURCE%" (
    echo ERROR: Build not found!
    echo Please run "python build.py" first, or check that dist\Inventory_Beta\ exists.
    pause
    exit /b 1
)

echo Installing to: %INSTALL_DIR%
echo.

:: Create directories
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\_internal" mkdir "%INSTALL_DIR%\_internal"
if not exist "%INSTALL_DIR%\data" mkdir "%INSTALL_DIR%\data"
if not exist "%INSTALL_DIR%\logs" mkdir "%INSTALL_DIR%\logs"

:: Copy files
echo Copying files...
copy /Y "%EXE_SOURCE%" "%INSTALL_DIR%\" >nul
xcopy /E /I /Y "%INTERNAL_SOURCE%" "%INSTALL_DIR%\_internal\" >nul
echo Files copied successfully.

:: Create Start Menu shortcut
echo Creating shortcuts...
set "SHORTCUT_SCRIPT=%TEMP%\create_shortcut.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%SHORTCUT_SCRIPT%"

:: Start Menu shortcut
echo sLinkFile = oWS.SpecialFolders("StartMenu") ^& "\Programs\Inventory Beta.lnk" >> "%SHORTCUT_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%SHORTCUT_SCRIPT%"
echo oLink.TargetPath = "%INSTALL_DIR%\Inventory_Beta.exe" >> "%SHORTCUT_SCRIPT%"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%SHORTCUT_SCRIPT%"
echo oLink.IconLocation = "%INSTALL_DIR%\Inventory_Beta.exe, 0" >> "%SHORTCUT_SCRIPT%"
echo oLink.Description = "Inventory Beta - Inventory Management System" >> "%SHORTCUT_SCRIPT%"
echo oLink.Save >> "%SHORTCUT_SCRIPT%"

:: Desktop shortcut
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\Inventory Beta.lnk" >> "%SHORTCUT_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%SHORTCUT_SCRIPT%"
echo oLink.TargetPath = "%INSTALL_DIR%\Inventory_Beta.exe" >> "%SHORTCUT_SCRIPT%"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%SHORTCUT_SCRIPT%"
echo oLink.IconLocation = "%INSTALL_DIR%\Inventory_Beta.exe, 0" >> "%SHORTCUT_SCRIPT%"
echo oLink.Description = "Inventory Beta - Inventory Management System" >> "%SHORTCUT_SCRIPT%"
echo oLink.Save >> "%SHORTCUT_SCRIPT%"

cscript "%SHORTCUT_SCRIPT%" /nologo
del "%SHORTCUT_SCRIPT%"

:: Add uninstall entry in Windows Settings
echo Adding uninstall entry...
set "UNINSTALL_KEY=HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inventory Beta"
reg add "%UNINSTALL_KEY%" /v "DisplayName" /t REG_SZ /d "Inventory Beta" /f >nul
reg add "%UNINSTALL_KEY%" /v "DisplayVersion" /t REG_SZ /d "1.3.0" /f >nul
reg add "%UNINSTALL_KEY%" /v "Publisher" /t REG_SZ /d "Inventory Pro" /f >nul
reg add "%UNINSTALL_KEY%" /v "DisplayIcon" /t REG_SZ /d "%INSTALL_DIR%\Inventory_Beta.exe,0" /f >nul
reg add "%UNINSTALL_KEY%" /v "UninstallString" /t REG_SZ /d "wscript.exe \"%INSTALL_DIR%\uninstall.vbs\"" /f >nul
reg add "%UNINSTALL_KEY%" /v "InstallLocation" /t REG_SZ /d "%INSTALL_DIR%" /f >nul
reg add "%UNINSTALL_KEY%" /v "NoModify" /t REG_DWORD /d 1 /f >nul
reg add "%UNINSTALL_KEY%" /v "NoRepair" /t REG_DWORD /d 1 /f >nul

:: Create uninstall script
echo Creating uninstaller...
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo Set oFS = CreateObject^("Scripting.FileSystemObject"^)
echo installDir = "%INSTALL_DIR%"
echo.
echo ' Remove shortcuts
echo desktop = oWS.SpecialFolders^("Desktop"^)
echo startMenu = oWS.SpecialFolders^("StartMenu"^)
echo If oFS.FileExists^(desktop ^& "\Inventory Beta.lnk"^) Then oFS.DeleteFile^(desktop ^& "\Inventory Beta.lnk"^)
echo If oFS.FileExists^(startMenu ^& "\Programs\Inventory Beta.lnk"^) Then oFS.DeleteFile^(startMenu ^& "\Programs\Inventory Beta.lnk"^)
echo.
echo ' Remove uninstall registry
echo oWS.Run "reg delete HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inventory Beta /f", 0, True
echo.
echo ' Remove app folder
echo If oFS.FolderExists^(installDir^) Then
echo   ' Keep data folder (ask user)
echo   keepData = MsgBox^("Keep your database and data files?", vbYesNo, "Uninstall Inventory Beta"^)
echo   If keepData = vbYes Then
echo     If oFS.FolderExists^(installDir ^& "\data"^) Then
echo       oFS.CopyFolder installDir ^& "\data", oWS.ExpandEnvironmentStrings^("%TEMP%\Inventory_Beta_Data"^)
echo     End If
echo   End If
echo   oFS.DeleteFolder installDir, True
echo End If
echo.
echo MsgBox "Inventory Beta has been uninstalled.", vbInformation, "Uninstall Complete"
) > "%INSTALL_DIR%\uninstall.vbs"

echo.
echo ============================================
echo    INSTALLATION COMPLETE!
echo ============================================
echo.
echo Inventory Beta has been installed to:
echo   %INSTALL_DIR%
echo.
echo Shortcuts created:
echo   - Desktop
echo   - Start Menu
echo.
echo To uninstall:
echo   - Run "%INSTALL_DIR%\uninstall.vbs"
echo   - Or go to Settings ^> Apps ^> Inventory Beta
echo.
echo You can now launch the app from the desktop shortcut.
echo.
pause
