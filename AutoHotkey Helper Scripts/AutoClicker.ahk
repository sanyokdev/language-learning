#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

#MaxThreadsPerHotKey, 2
Toggle :=0
F2::
Toggle :=!Toggle
While (Toggle=1)
{
	Click, Left
	sleep, 50
}
return