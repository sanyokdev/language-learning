#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

NumpadMult::
Clipboard := ""		;Clear the clipboard
Send, ^c			;Copy (Ctrl+C)
ClipWait, 2			;Wait for the clipboard to contain data
if (ErrorLevel){	;If ClipWait failed
	return
}
FileAppend, % Clipboard, D:\Dev\ClipboardSave\saved.html