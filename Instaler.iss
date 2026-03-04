; Script oficial para o instalador BtG System
; Organizado por Gemini 3 Flash

#define MyAppName "BtG System Trial"
#define MyAppVersion "1.0"
#define MyAppPublisher "netimero labs"
#define MyAppExeName "BtGSys.exe"
#define MyAppAssocName MyAppName + " File"
#define MyAppAssocExt ".myp"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; NOTE: O AppId identifica unicamente este aplicativo.
AppId={{DAE0E488-C477-4A51-8AF2-39CC88C7AEF3}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ChangesAssociations=yes
DisableProgramGroupPage=yes
OutputBaseFilename=BtG System Trial Installer
SolidCompression=yes
WizardStyle=modern dynamic
; Define o ícone de corrida para o próprio instalador
SetupIconFile=C:\Users\Bruno\OneDrive\Documentos\Carreira\PUCPR\Práticas de Extensão\PROJETO2 - EM ANDAMENTO\BtG System\iconapplication.ico

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Executável principal (da pasta dist)
Source: "C:\Users\Bruno\OneDrive\Documentos\Carreira\PUCPR\Práticas de Extensão\PROJETO2 - EM ANDAMENTO\BtG System\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Imagens auxiliares (caso precise carregar por fora do executável)
Source: "C:\Users\Bruno\OneDrive\Documentos\Carreira\PUCPR\Práticas de Extensão\PROJETO2 - EM ANDAMENTO\BtG System\btg.png"; DestDir: "{app}"; Flags: ignoreversion

; Pastas de modelos e pacientes - Note o DestDir corrigido para criar subpastas
Source: "C:\Users\Bruno\OneDrive\Documentos\Carreira\PUCPR\Práticas de Extensão\PROJETO2 - EM ANDAMENTO\BtG System\modelos\*"; DestDir: "{app}\modelos"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\Bruno\OneDrive\Documentos\Carreira\PUCPR\Práticas de Extensão\PROJETO2 - EM ANDAMENTO\BtG System\pacientes\*"; DestDir: "{app}\pacientes"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

[Dirs]
; ESSENCIAL: Permissões de escrita para o banco de dados e fotos de pacientes
Name: "{app}"; Permissions: users-modify
Name: "{app}\pacientes"; Permissions: users-modify
Name: "{app}\modelos"; Permissions: users-modify

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

[Registry]
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent