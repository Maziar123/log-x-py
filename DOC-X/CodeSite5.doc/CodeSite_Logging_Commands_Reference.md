# CodeSite Logging Commands Reference

Complete reference of `TCodeSiteLogger` methods for Delphi/Pascal (.pas) files.

Global instance: `CodeSite` (automatically available after adding `CodeSiteLogging` to uses clause)

---

## 1. Basic Message Sending

| Method | Description | Example |
|--------|-------------|---------|
| `Send(Msg)` | Simple text message | `CodeSite.Send('Hello World');` |
| `Send(MsgType, Msg)` | Message with icon type | `CodeSite.Send(csmInfo, 'Processing...');` |
| `Send(Msg, Value)` | Message with data value | `CodeSite.Send('Counter', Counter);` |
| `SendMsg(Msg)` | Simple message (no timestamp details) | `CodeSite.SendMsg('Checkpoint');` |
| `SendMsg(MsgType, Msg)` | Message with custom type | `CodeSite.SendMsg(csmWarning, 'Alert');` |
| `SendNote(Msg)` | Note message (blue icon) | `CodeSite.SendNote('Remember to save');` |
| `SendReminder(Msg)` | Reminder message | `CodeSite.SendReminder('TODO: Fix bug #123');` |

### Message Type Constants (Icons)
| Constant | Icon Color | Usage |
|----------|-----------|-------|
| `csmDefault` | Default | General messages |
| `csmInfo` | Blue | Information |
| `csmWarning` | Yellow/Orange | Warnings |
| `csmError` | Red | Errors |
| `csmGreen` | Green | Success/Start |
| `csmCheckPoint` | Checkpoint | Progress markers |
| `csmBlue`, `csmRed`, `csmYellow` | Various | Color-coded messages |

---

## 2. Method Tracing (Call Stack)

| Method | Description | Example |
|--------|-------------|---------|
| `EnterMethod(MethodName)` | Mark start of method | `CodeSite.EnterMethod('LoadData');` |
| `EnterMethod(Obj, MethodName)` | With object context | `CodeSite.EnterMethod(Self, 'ButtonClick');` |
| `ExitMethod` | Mark end of method | `CodeSite.ExitMethod;` |
| `ExitMethodCollapse` | Exit + collapse messages | `CodeSite.ExitMethodCollapse;` |
| `TraceMethod(Obj, MethodName)` | Auto entry/exit | `CodeSite.TraceMethod(Self, 'Process');` |
| `TraceMethodCollapse` | Auto with collapse | `CodeSite.TraceMethodCollapse;` |

### Usage Pattern:
```pascal
procedure TForm1.LoadData;
begin
  CodeSite.EnterMethod('LoadData');
  try
    // ... method code ...
  finally
    CodeSite.ExitMethod;
  end;
end;
```

---

## 3. Error & Warning Messages

| Method | Description | Example |
|--------|-------------|---------|
| `SendError(Msg)` | Error message (red icon) | `CodeSite.SendError('Connection failed');` |
| `SendError(Msg, Value)` | Error with value | `CodeSite.SendError('Failed ID', ID);` |
| `SendWarning(Msg)` | Warning message (yellow) | `CodeSite.SendWarning('Low disk space');` |
| `SendException(E)` | Log exception details | `CodeSite.SendException(E);` |
| `SendException(E, Msg)` | Exception with context | `CodeSite.SendException(E, 'In LoadData');` |
| `LogError(Msg)` | Standard error logging | `CodeSite.LogError('Database error');` |
| `LogWarning(Msg)` | Standard warning logging | `CodeSite.LogWarning('Deprecated API');` |
| `LogEvent(Msg)` | Log event | `CodeSite.LogEvent('User logged in');` |

---

## 4. System & Memory Information

| Method | Description | Example |
|--------|-------------|---------|
| `SendSystemInfo` | OS version, memory, etc. | `CodeSite.SendSystemInfo;` |
| `SendMemoryStatus` | System memory info | `CodeSite.SendMemoryStatus;` |
| `SendHeapStatus` | Delphi heap status | `CodeSite.SendHeapStatus;` |
| `SendMemoryManagerStatus` | Memory manager stats | `CodeSite.SendMemoryManagerStatus;` |
| `SendMemoryAsHex(Ptr, Size)` | Hex dump of memory | `CodeSite.SendMemoryAsHex(@Buffer, 256);` |
| `SendStackTrace` | Current call stack | `CodeSite.SendStackTrace;` |
| `SendWindowHandle(Handle)` | Window handle info | `CodeSite.SendWindowHandle(Handle);` |
| `SendScreenshot` | Capture screen | `CodeSite.SendScreenshot;` |
| `SendParents(Control)` | Parent hierarchy | `CodeSite.SendParents(Edit1);` |

---

## 5. File & Stream Operations

| Method | Description | Example |
|--------|-------------|---------|
| `SendFileAsHex(FileName)` | Hex dump of file | `CodeSite.SendFileAsHex('data.bin');` |
| `SendTextFile(FileName)` | Text file contents | `CodeSite.SendTextFile('config.ini');` |
| `SendStreamAsHex(Stream)` | Hex dump of stream | `CodeSite.SendStreamAsHex(MemoryStream);` |
| `SendStreamAsText(Stream)` | Stream as text | `CodeSite.SendStreamAsText(StringStream);` |

---

## 6. Data Type Specific

| Method | Description | Example |
|--------|-------------|---------|
| `SendColor(Msg, Color)` | TColor value | `CodeSite.SendColor('Form.Color', clBlue);` |
| `SendCurrency(Msg, Value)` | Currency type | `CodeSite.SendCurrency('Price', 19.99);` |
| `SendDateTime(Msg, Value)` | TDateTime | `CodeSite.SendDateTime('Now', Now);` |
| `SendDateTimeIf(Cond, Msg, Value)` | Conditional datetime | `CodeSite.SendDateTimeIf(Debug, 'Time', Now);` |
| `SendEnum(Msg, Enum)` | Enumeration | `CodeSite.SendEnum('State', dsEdit);` |
| `SendSet(Msg, Set)` | Set type | `CodeSite.SendSet('Options', [optA, optB]);` |
| `SendPointer(Msg, Ptr)` | Pointer address | `CodeSite.SendPointer('Obj', @Object);` |
| `SendVariant(Msg, Var)` | Variant value | `CodeSite.SendVariant('Data', VariantVar);` |
| `SendKey` | Virtual key code | `CodeSite.SendKey;` |
| `SendMouseButton` | Mouse button state | `CodeSite.SendMouseButton;` |
| `SendCurrency(Msg, Value)` | Currency value | `CodeSite.SendCurrency('Amount', Amount);` |

---

## 7. Component & Object Information

| Method | Description | Example |
|--------|-------------|---------|
| `Send(Msg, Obj)` | Object properties | `CodeSite.Send('MainForm', Self);` |
| `SendComponents(Comp)` | Component list | `CodeSite.SendComponents(Form1);` |
| `SendComponentAsText(Comp)` | Component details | `CodeSite.SendComponentAsText(Button1);` |
| `SendControls(Control)` | Child controls | `CodeSite.SendControls(Panel1);` |
| `SendParents(Control)` | Parent hierarchy | `CodeSite.SendParents(Edit1);` |
| `SendProperty(Obj, PropName)` | Single property | `CodeSite.SendProperty(Self, 'Caption');` |
| `SendCollection(Coll)` | Collection items | `CodeSite.SendCollection(Strings);` |
| `SendAssigned(Msg, Ptr)` | Check if assigned | `CodeSite.SendAssigned('Dataset', Dataset);` |
| `SendParents(Control)` | Parent chain | `CodeSite.SendParents(Button1);` |

---

## 8. Registry & Version Info

| Method | Description | Example |
|--------|-------------|---------|
| `SendRegistry(Root, Key)` | Registry contents | `CodeSite.SendRegistry(HKEY_CURRENT_USER, '\Software');` |
| `SendVersionInfo(FileName)` | File version info | `CodeSite.SendVersionInfo('myapp.exe');` |
| `SendFileVersionInfo(File)` | Detailed version | `CodeSite.SendFileVersionInfo(Application.ExeName);` |
| `SendWinError(ErrorCode)` | Windows error | `CodeSite.SendWinError(GetLastError);` |

---

## 9. XML Data

| Method | Description | Example |
|--------|-------------|---------|
| `SendXMLData(Msg, XML)` | XML string data | `CodeSite.SendXMLData('Config', XMLStr);` |
| `SendXMLFile(FileName)` | XML file contents | `CodeSite.SendXMLFile('config.xml');` |

---

## 10. Conditional & Formatted Sending

| Method | Description | Example |
|--------|-------------|---------|
| `SendIf(Cond, Msg, Value)` | Send only if true | `CodeSite.SendIf(Count>0, 'Count', Count);` |
| `SendAssigned(Ptr, Msg)` | Send if not nil | `CodeSite.SendAssigned(List, 'List');` |
| `SendFmtMsg(Format, Args)` | Formatted message | `CodeSite.SendFmtMsg('ID=%d, Name=%s', [ID, Name]);` |
| `Sending(Category)` | Check if enabled | `if CodeSite.Sending('Debug') then ...` |
| `SendIf(Cond, Msg, Value)` | Conditional send | `CodeSite.SendIf(Debug, 'Info', Data);` |

---

## 11. Checkpoints & Separators

| Method | Description | Example |
|--------|-------------|---------|
| `AddCheckpoint` | Add checkpoint marker | `CodeSite.AddCheckpoint;` |
| `ResetCheckpoint` | Reset checkpoint counter | `CodeSite.ResetCheckpoint;` |
| `CheckpointCounter` | Get checkpoint count | `N := CodeSite.CheckpointCounter;` |
| `AddSeparator` | Add visual separator | `CodeSite.AddSeparator;` |
| `Clear` | Clear the log | `CodeSite.Clear;` |

---

## 12. Write Methods (No Timestamp)

| Method | Description | Example |
|--------|-------------|---------|
| `Write(Msg, Value)` | Write without timestamp | `CodeSite.Write('Label', Value);` |
| `WriteColor(Msg, Color)` | Write color value | `CodeSite.WriteColor('Color', clRed);` |
| `WriteCurrency(Msg, Value)` | Write currency | `CodeSite.WriteCurrency('Price', 10.50);` |
| `WriteDateTime(Msg, Value)` | Write datetime | `CodeSite.WriteDateTime('Date', Now);` |

---

## 13. Category Management

| Method | Description | Example |
|--------|-------------|---------|
| `Category` | Set category for logger | `CodeSite.Category := 'Database';` |
| `CategoryColor` | Set category color | `CodeSite.CategoryColor := csmBlue;` |
| `CategoryBackColor` | Background color | `CodeSite.CategoryBackColor := clYellow;` |
| `CategoryForeColor` | Foreground color | `CodeSite.CategoryForeColor := clRed;` |
| `CategoryFontColor` | Font color | `CodeSite.CategoryFontColor := clBlack;` |

---

## Complete Working Example

```pascal
unit MainFormUnit;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants,
  System.Classes, Vcl.Graphics, Vcl.Controls, Vcl.Forms, Vcl.Dialogs,
  Vcl.StdCtrls, CodeSiteLogging;  // <-- Add this

type
  TForm1 = class(TForm)
    Button1: TButton;
    procedure Button1Click(Sender: TObject);
    procedure FormCreate(Sender: TObject);
  private
    procedure LoadUserData(UserID: Integer);
  end;

var
  Form1: TForm1;

implementation

{$R *.dfm}

procedure TForm1.FormCreate(Sender: TObject);
begin
  // Configure category
  CodeSite.Category := 'MainForm';
  CodeSite.CategoryColor := csmGreen;
  CodeSite.Send('Application started');
end;

procedure TForm1.Button1Click(Sender: TObject);
begin
  CodeSite.EnterMethod(Self, 'Button1Click');
  try
    CodeSite.Send('Button clicked');
    CodeSite.Send('Sender class', Sender.ClassName);
    
    LoadUserData(123);
    
    CodeSite.SendNote('Processing complete');
  except
    on E: Exception do
    begin
      CodeSite.SendException(E, 'In Button1Click');
      raise;
    end;
  end;
  CodeSite.ExitMethod;
end;

procedure TForm1.LoadUserData(UserID: Integer);
begin
  CodeSite.EnterMethod('LoadUserData');
  try
    CodeSite.Send('UserID', UserID);
    CodeSite.SendDateTime('Start time', Now);
    
    if UserID <= 0 then
    begin
      CodeSite.SendWarning('Invalid UserID');
      Exit;
    end;
    
    // ... load data ...
    
    CodeSite.SendCheckpoint;
    CodeSite.Send('Data loaded successfully');
  finally
    CodeSite.ExitMethod;
  end;
end;

end.
```

---

## Related Documentation Files

| Topic | File |
|-------|------|
| CodeSite Logging System Overview | [00-Overview/codesiteloggingsystem.htm](00-Overview/codesiteloggingsystem.htm) |
| TCodeSiteLogger Class | [01-Classes-Logger/tcodesitelogger.htm](01-Classes-Logger/tcodesitelogger.htm) |
| TCodeSiteLogger Methods | [01-Classes-Logger/tcodesitelogger_methods.htm](01-Classes-Logger/tcodesitelogger_methods.htm) |
| TCodeSiteLogger Properties | [01-Classes-Logger/tcodesitelogger_properties.htm](01-Classes-Logger/tcodesitelogger_properties.htm) |
| Message Types | [00-Overview/messagetypes.htm](00-Overview/messagetypes.htm) |
| Destination Classes | [02-Classes-Destinations/](02-Classes-Destinations/) |
| File Logging Guide | [00-Overview/filelogging.htm](00-Overview/filelogging.htm) |
| Live Logging Guide | [00-Overview/livelogging.htm](00-Overview/livelogging.htm) |

---

## HTML File Locations by Category

| Category | Directory |
|----------|-----------|
| Overview & Guides | `00-Overview/` |
| TCodeSiteLogger (all methods) | `01-Classes-Logger/` |
| Destination Classes | `02-Classes-Destinations/` |
| Formatter | `03-Classes-Formatter/` |
| CodeSiteManager | `05-CodeSiteManager/` |
| Viewer | `06-Viewer/` |
| Dispatcher | `07-Dispatcher/` |
| Controller | `08-Controller/` |

---

*Generated from CodeSite 5 Help Documentation*
