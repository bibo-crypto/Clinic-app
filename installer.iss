; ═══════════════════════════════════════════════════════════════════════════
;  Inno Setup Script — Clinic Management System Installer
;  Requirements: Inno Setup 6.x  (https://jrsoftware.org/isinfo.php)
;  Usage: Open this file in Inno Setup Compiler → Build → Compile
;         OR run: ISCC.exe installer.iss
;  Output: output\ClinicSetup.exe
; ═══════════════════════════════════════════════════════════════════════════

#define AppName      "Clinic Management System"
#define AppVersion   "1.0.0"
#define AppPublisher "BiboMarcos"
#define AppURL       "https://github.com/bibo-crypto"
#define AppExeName   "ClinicSystem.exe"
#define AppExeDir    "dist\ClinicSystem"

[Setup]
; ── Identity ─────────────────────────────────────────────────────────────────
AppId={{A3F7C2D1-84BE-4E5A-9F2B-0C61D3E8A7F4}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; ── Installer behavior ────────────────────────────────────────────────────────
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; ── Output ────────────────────────────────────────────────────────────────────
OutputDir=output
OutputBaseFilename=ClinicSetup
SetupIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
CompressionThreads=auto

; ── Wizard appearance ─────────────────────────────────────────────────────────
WizardStyle=modern

; ── Misc ──────────────────────────────────────────────────────────────────────
ArchitecturesInstallIn64BitMode=x64compatible
ShowLanguageDialog=yes
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}
VersionInfoVersion={#AppVersion}
VersionInfoDescription={#AppName} Installer
VersionInfoProductName={#AppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; ── Main application folder ───────────────────────────────────────────────────
Source: "{#AppExeDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; ── Start Menu ────────────────────────────────────────────────────────────────
Name: "{group}\{#AppName}";          Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"

; ── Desktop shortcut ──────────────────────────────────────────────────────────
Name: "{autodesktop}\{#AppName}";    Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"; Tasks: desktopicon


[Run]
; ── Launch after install ──────────────────────────────────────────────────────
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; ── Remove the database and exports created at runtime ────────────────────────
Type: filesandordirs; Name: "{app}\database\clinic.db"
Type: filesandordirs; Name: "{app}\exports"
Type: filesandordirs; Name: "{app}\backups"

[Code]
// ── Custom code: show a friendly finish message ──────────────────────────────
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Nothing extra needed — database is created on first run
  end;
end;
