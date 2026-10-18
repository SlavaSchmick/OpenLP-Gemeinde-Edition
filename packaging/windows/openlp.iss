; OpenLP Gemeinde-Edition - Windows installer (Inno Setup 6), built by build.ps1
;
; Installs the Gemeinde-Edition, a modified version of OpenLP, with the Live Video plugin, the audio output selection,
; the faster Bible and song search and the English, German, Russian and Ukrainian user interface. An existing
; installation of the official OpenLP is removed first; the user's data, settings and songs in %APPDATA%\openlp are
; kept. Installed silently (as the update of OpenLP does), it starts OpenLP again at the end.

#ifndef AppVersion
  #define AppVersion "3.1.7+gemeinde.1"
#endif
#ifndef AppVersionNumeric
  #define AppVersionNumeric "3.1.7.1"
#endif
#ifndef AppFileVersion
  #define AppFileVersion "3.1.7-gemeinde.1"
#endif
#ifndef ProductName
  #define ProductName "OpenLP Gemeinde-Edition"
#endif
#ifndef ProductUrl
  #define ProductUrl "https://openlp.org/"
#endif
#ifndef SourceDir
  #define SourceDir "dist\OpenLP"
#endif
#ifndef RepoDir
  #define RepoDir "..\.."
#endif

[Setup]
; The AppId of the official OpenLP Inno Setup installers, so that an installation made by one of them is updated
AppId={{AA7699FA-B2D2-43F4-8A70-D497D03C9485}
AppName={#ProductName}
AppVersion={#AppVersion}
AppVerName={#ProductName} {#AppVersion}
AppPublisher={#ProductName} (modified OpenLP)
AppPublisherURL={#ProductUrl}
AppSupportURL={#ProductUrl}
AppUpdatesURL={#ProductUrl}
DefaultDirName={autopf}\OpenLP
DefaultGroupName=OpenLP
DisableProgramGroupPage=yes
LicenseFile={#RepoDir}\LICENSE
OutputBaseFilename=OpenLP-Gemeinde-Edition-{#AppFileVersion}-Setup-x64
SetupIconFile={#RepoDir}\resources\images\OpenLP.ico
UninstallDisplayIcon={app}\OpenLP.exe
UninstallDisplayName={#ProductName} {#AppVersion}
Compression=lzma2/max
SolidCompression=yes
LZMANumBlockThreads=4
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
MinVersion=10.0
CloseApplications=force
ChangesAssociations=yes
ShowLanguageDialog=auto
LanguageDetectionMethod=uilanguage
VersionInfoVersion={#AppVersionNumeric}
VersionInfoProductName={#ProductName}
VersionInfoProductTextVersion={#AppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"

[CustomMessages]
english.RemovingOld=Removing the previous OpenLP installation...
german.RemovingOld=Die bisherige OpenLP-Installation wird entfernt...
russian.RemovingOld=Удаление предыдущей установки OpenLP...
ukrainian.RemovingOld=Видалення попередньої інсталяції OpenLP...
english.RemoveFailed=The previous OpenLP installation could not be removed (error %1). Please uninstall it in the Windows settings and start this setup again.
german.RemoveFailed=Die bisherige OpenLP-Installation konnte nicht entfernt werden (Fehler %1). Bitte deinstallieren Sie sie in den Windows-Einstellungen und starten Sie dieses Setup erneut.
russian.RemoveFailed=Не удалось удалить предыдущую установку OpenLP (ошибка %1). Удалите её в параметрах Windows и снова запустите эту установку.
ukrainian.RemoveFailed=Не вдалося видалити попередню інсталяцію OpenLP (помилка %1). Видаліть її в параметрах Windows і знову запустіть цю інсталяцію.
english.WaitingForOpenLP=Waiting for OpenLP to close...
german.WaitingForOpenLP=Warten, bis OpenLP beendet ist...
russian.WaitingForOpenLP=Ожидание завершения OpenLP...
ukrainian.WaitingForOpenLP=Очікування завершення OpenLP...
english.OpenLPStillRunning=OpenLP is still running and could not be closed. Nothing has been changed. Please close OpenLP and start this setup again.
german.OpenLPStillRunning=OpenLP läuft noch und konnte nicht beendet werden. Es wurde nichts verändert. Bitte beenden Sie OpenLP und starten Sie dieses Setup erneut.
russian.OpenLPStillRunning=OpenLP всё ещё работает, и его не удалось закрыть. Ничего не изменено. Закройте OpenLP и снова запустите эту установку.
ukrainian.OpenLPStillRunning=OpenLP усе ще працює, і його не вдалося закрити. Нічого не змінено. Закрийте OpenLP і знову запустіть цю інсталяцію.
english.CloseOpenLP=OpenLP is running. Please close OpenLP (save the service if needed) and click "Retry".
german.CloseOpenLP=OpenLP ist geöffnet. Bitte beenden Sie OpenLP (den Ablauf ggf. vorher speichern) und klicken Sie auf „Wiederholen“.
russian.CloseOpenLP=OpenLP открыт. Закройте OpenLP (при необходимости сохраните служение) и нажмите «Повторить».
ukrainian.CloseOpenLP=OpenLP відкрито. Закрийте OpenLP (за потреби збережіть служіння) і натисніть «Повторити».
english.AssociateFiles=Open OpenLP service files (.osz, .oszl) with OpenLP
german.AssociateFiles=OpenLP-Ablaufdateien (.osz, .oszl) mit OpenLP öffnen
russian.AssociateFiles=Открывать файлы служения OpenLP (.osz, .oszl) в OpenLP
ukrainian.AssociateFiles=Відкривати файли служіння OpenLP (.osz, .oszl) в OpenLP
english.ServiceFile=OpenLP Service
german.ServiceFile=OpenLP-Ablauf
russian.ServiceFile=Служение OpenLP
ukrainian.ServiceFile=Служіння OpenLP

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "associate"; Description: "{cm:AssociateFiles}"; GroupDescription: "{cm:AdditionalIcons}"

[InstallDelete]
; Files of an older version which are not part of this one
Type: filesandordirs; Name: "{app}\plugins"
Type: filesandordirs; Name: "{app}\core"
Type: filesandordirs; Name: "{app}\i18n"
; The shortcuts of an older version, which were just called "OpenLP"
Type: files; Name: "{group}\OpenLP.lnk"
Type: files; Name: "{group}\{cm:UninstallProgram,OpenLP}.lnk"
Type: files; Name: "{autodesktop}\OpenLP.lnk"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#ProductName}"; Filename: "{app}\OpenLP.exe"
Name: "{group}\{cm:UninstallProgram,{#ProductName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#ProductName}"; Filename: "{app}\OpenLP.exe"; Tasks: desktopicon

[Registry]
Root: HKA; Subkey: "Software\Classes\.osz"; ValueType: string; ValueName: ""; ValueData: "OpenLP.Service"; Flags: uninsdeletevalue; Tasks: associate
Root: HKA; Subkey: "Software\Classes\.oszl"; ValueType: string; ValueName: ""; ValueData: "OpenLP.Service"; Flags: uninsdeletevalue; Tasks: associate
Root: HKA; Subkey: "Software\Classes\OpenLP.Service"; ValueType: string; ValueName: ""; ValueData: "{cm:ServiceFile}"; Flags: uninsdeletekey; Tasks: associate
Root: HKA; Subkey: "Software\Classes\OpenLP.Service\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\OpenLP.exe,0"; Tasks: associate
Root: HKA; Subkey: "Software\Classes\OpenLP.Service\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\OpenLP.exe"" ""%1"""; Tasks: associate

[Run]
Filename: "{app}\OpenLP.exe"; Description: "{cm:LaunchProgram,{#ProductName}}"; Flags: nowait postinstall skipifsilent
; After an update from within OpenLP (a silent installation) OpenLP is started again, as the user and not as admin
Filename: "{app}\OpenLP.exe"; Flags: nowait runasoriginaluser skipifnotsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
const
  UninstallKey = 'Software\Microsoft\Windows\CurrentVersion\Uninstall';
  OwnKey = '{AA7699FA-B2D2-43F4-8A70-D497D03C9485}_is1';

{ Remove the double quotes around a path }
function Unquote(Value: String): String;
begin
  Result := Trim(Value);
  if (Length(Result) >= 2) and (Result[1] = '"') then
  begin
    Delete(Result, 1, 1);
    if Pos('"', Result) > 0 then
      Result := Copy(Result, 1, Pos('"', Result) - 1);
  end;
end;

{ Uninstall another installation of OpenLP which is registered under the given key, an MSI or an Inno Setup one }
function RemoveInstallation(RootKey: Integer; Key: String; var ErrorCode: Integer): Boolean;
var
  Command: String;
  IsMsi: Cardinal;
begin
  Result := True;
  if RegQueryDWordValue(RootKey, UninstallKey + '\' + Key, 'WindowsInstaller', IsMsi) and (IsMsi = 1) then
  begin
    Result := Exec(ExpandConstant('{sys}\msiexec.exe'), '/x ' + Key + ' /qn /norestart', '', SW_HIDE,
                   ewWaitUntilTerminated, ErrorCode) and ((ErrorCode = 0) or (ErrorCode = 3010) or (ErrorCode = 1605));
  end
  else if RegQueryStringValue(RootKey, UninstallKey + '\' + Key, 'UninstallString', Command) then
  begin
    Result := Exec(Unquote(Command), '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART', '', SW_HIDE,
                   ewWaitUntilTerminated, ErrorCode) and (ErrorCode = 0);
  end;
end;

{ Find and remove installations of the official OpenLP in one part of the registry }
function RemoveFrom(RootKey: Integer; var ErrorCode: Integer): Boolean;
var
  Keys: TArrayOfString;
  Name: String;
  Index: Integer;
begin
  Result := True;
  if not RegGetSubkeyNames(RootKey, UninstallKey, Keys) then
    exit;
  for Index := 0 to GetArrayLength(Keys) - 1 do
  begin
    if CompareText(Keys[Index], OwnKey) = 0 then
      continue;
    if RegQueryStringValue(RootKey, UninstallKey + '\' + Keys[Index], 'DisplayName', Name) and
       (CompareText(Copy(Name, 1, 6), 'OpenLP') = 0) then
    begin
      Log('Removing ' + Name + ' (' + Keys[Index] + ')');
      if not RemoveInstallation(RootKey, Keys[Index], ErrorCode) then
      begin
        Result := False;
        exit;
      end;
    end;
  end;
end;

{ Whether a program OpenLP.exe is running, e.g. OpenLP which is still closing after it started this setup for an
  update }
function IsOpenLPRunning(): Boolean;
var
  Locator, Service, Processes: Variant;
begin
  Result := False;
  try
    Locator := CreateOleObject('WbemScripting.SWbemLocator');
    Service := Locator.ConnectServer('.', 'root\CIMV2');
    Processes := Service.ExecQuery('SELECT ProcessId FROM Win32_Process WHERE Name = ''OpenLP.exe''');
    Result := Processes.Count > 0;
  except
    Log('The running programs could not be checked: ' + GetExceptionMessage);
  end;
end;

{ Wait until OpenLP is closed, and end it if it still runs after a minute. The old program files are deleted at the
  start of the installation; while OpenLP runs, its files can't be replaced, and the installation would stop halfway
  with the old files already gone. }
function WaitForOpenLP(): Boolean;
var
  Waited, ResultCode: Integer;
begin
  if not WizardSilent() then
  begin
    { Started by hand: ask to close OpenLP, it may have unsaved changes }
    while IsOpenLPRunning() do
      if MsgBox(CustomMessage('CloseOpenLP'), mbInformation, MB_RETRYCANCEL) = IDCANCEL then
      begin
        Result := False;
        exit;
      end;
    Result := True;
    exit;
  end;
  { An update from within OpenLP: OpenLP is closing, it already asked to save the service }
  Waited := 0;
  while IsOpenLPRunning() and (Waited < 60) do
  begin
    if Waited = 0 then
    begin
      Log('Waiting for OpenLP to close');
      WizardForm.StatusLabel.Caption := CustomMessage('WaitingForOpenLP');
    end;
    Sleep(1000);
    Waited := Waited + 1;
  end;
  if IsOpenLPRunning() then
  begin
    Log('OpenLP is still running after a minute, ending it');
    Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /T /IM OpenLP.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Waited := 0;
    while IsOpenLPRunning() and (Waited < 15) do
    begin
      Sleep(1000);
      Waited := Waited + 1;
    end;
  end;
  Result := not IsOpenLPRunning();
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ErrorCode: Integer;
begin
  Result := '';
  ErrorCode := 0;
  if not WaitForOpenLP() then
  begin
    Result := CustomMessage('OpenLPStillRunning');
    exit;
  end;
  WizardForm.StatusLabel.Caption := CustomMessage('RemovingOld');
  if not (RemoveFrom(HKLM64, ErrorCode) and RemoveFrom(HKLM32, ErrorCode) and RemoveFrom(HKCU, ErrorCode)) then
    Result := FmtMessage(CustomMessage('RemoveFailed'), [IntToStr(ErrorCode)]);
end;
