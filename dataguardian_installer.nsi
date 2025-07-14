; DataGuardian Pro NSIS Installer Script
; Creates a professional Windows installer for DataGuardian Pro

!include "MUI2.nsh"
!include "FileFunc.nsh"

;--------------------------------
; General Settings
Name "DataGuardian Pro"
OutFile "DataGuardian-Pro-Setup.exe"
InstallDir "$PROGRAMFILES\DataGuardian Pro"
InstallDirRegKey HKCU "Software\DataGuardian-Pro" ""
RequestExecutionLevel admin

;--------------------------------
; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "static\icon.ico"
!define MUI_UNICON "static\icon.ico"

;--------------------------------
; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Languages
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Dutch"

;--------------------------------
; Installer Sections
Section "DataGuardian Pro" SecMain
    SetOutPath $INSTDIR
    
    ; Main executable and startup script
    File "DataGuardian Pro.exe"
    File "run_dataguardian.bat"
    
    ; Configuration files
    SetOutPath $INSTDIR\config
    File /nonfatal ".env.example"
    
    ; Documentation
    SetOutPath $INSTDIR\documentation
    File /nonfatal "README.txt"
    File /nonfatal "User_Guide.pdf"
    File /nonfatal "WINDOWS_DEPLOYMENT_GUIDE.md"
    
    ; Create application data directory
    CreateDirectory "$APPDATA\DataGuardian Pro"
    CreateDirectory "$APPDATA\DataGuardian Pro\logs"
    CreateDirectory "$APPDATA\DataGuardian Pro\reports"
    CreateDirectory "$APPDATA\DataGuardian Pro\data"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\DataGuardian Pro"
    CreateShortcut "$SMPROGRAMS\DataGuardian Pro\DataGuardian Pro.lnk" "$INSTDIR\run_dataguardian.bat" "" "$INSTDIR\DataGuardian Pro.exe"
    CreateShortcut "$SMPROGRAMS\DataGuardian Pro\User Guide.lnk" "$INSTDIR\documentation\User_Guide.pdf"
    CreateShortcut "$SMPROGRAMS\DataGuardian Pro\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    
    ; Desktop shortcut (optional)
    CreateShortcut "$DESKTOP\DataGuardian Pro.lnk" "$INSTDIR\run_dataguardian.bat" "" "$INSTDIR\DataGuardian Pro.exe"
    
    ; Registry entries
    WriteRegStr HKCU "Software\DataGuardian-Pro" "" $INSTDIR
    WriteRegStr HKCU "Software\DataGuardian-Pro" "Version" "1.0.0"
    WriteRegStr HKCU "Software\DataGuardian-Pro" "InstallDate" "$DATE"
    
    ; Uninstall registry entries
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\DataGuardian-Pro" "DisplayName" "DataGuardian Pro"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\DataGuardian-Pro" "DisplayVersion" "1.0.0"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\DataGuardian-Pro" "Publisher" "DataGuardian Pro"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\DataGuardian-Pro" "DisplayIcon" "$INSTDIR\DataGuardian Pro.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\DataGuardian-Pro" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\DataGuardian-Pro" "NoModify" "1"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\DataGuardian-Pro" "NoRepair" "1"
    
    ; Get installation size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\DataGuardian-Pro" "EstimatedSize" "$0"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Windows Firewall rule (optional)
    ExecWait 'netsh advfirewall firewall add rule name="DataGuardian Pro" dir=in action=allow protocol=TCP localport=5000'
    
SectionEnd

;--------------------------------
; Uninstaller Section
Section "Uninstall"
    
    ; Remove files
    Delete "$INSTDIR\DataGuardian Pro.exe"
    Delete "$INSTDIR\run_dataguardian.bat"
    Delete "$INSTDIR\Uninstall.exe"
    
    ; Remove directories
    RMDir /r "$INSTDIR\config"
    RMDir /r "$INSTDIR\documentation"
    RMDir "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\DataGuardian Pro\DataGuardian Pro.lnk"
    Delete "$SMPROGRAMS\DataGuardian Pro\User Guide.lnk"
    Delete "$SMPROGRAMS\DataGuardian Pro\Uninstall.lnk"
    RMDir "$SMPROGRAMS\DataGuardian Pro"
    Delete "$DESKTOP\DataGuardian Pro.lnk"
    
    ; Remove registry entries
    DeleteRegKey HKCU "Software\DataGuardian-Pro"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\DataGuardian-Pro"
    
    ; Remove firewall rule
    ExecWait 'netsh advfirewall firewall delete rule name="DataGuardian Pro"'
    
    ; Optional: Remove user data (ask user first)
    MessageBox MB_YESNO "Do you want to remove all user data and reports?" IDNO +2
    RMDir /r "$APPDATA\DataGuardian Pro"
    
SectionEnd

;--------------------------------
; Functions
Function .onInit
    ; Check if already installed
    ReadRegStr $R0 HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\DataGuardian-Pro" "UninstallString"
    StrCmp $R0 "" done
    
    MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION "DataGuardian Pro is already installed. $\n$\nClick OK to remove the previous version or Cancel to cancel this upgrade." IDOK uninst
    Abort
    
    uninst:
        ClearErrors
        ExecWait '$R0 /S _?=$INSTDIR'
        
        IfErrors no_remove_uninstaller done
        no_remove_uninstaller:
    
    done:
FunctionEnd

Function un.onInit
    MessageBox MB_YESNO "Are you sure you want to completely remove DataGuardian Pro and all of its components?" IDYES +2
    Abort
FunctionEnd

;--------------------------------
; Version Information
VIProductVersion "1.0.0.0"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "DataGuardian Pro"
VIAddVersionKey /LANG=${LANG_ENGLISH} "CompanyName" "DataGuardian Pro"
VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "Copyright (c) 2025 DataGuardian Pro"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "DataGuardian Pro Installer"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "1.0.0.0"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductVersion" "1.0.0.0"