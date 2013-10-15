'---------------------------------------------------------------------------------
' The sample scripts are not supported under any Microsoft standard support
' program or service. The sample scripts are provided AS IS without warranty
' of any kind. Microsoft further disclaims all implied warranties including,
' without limitation, any implied warranties of merchantability or of fitness for
' a particular purpose. The entire risk arising out of the use or performance of
' the sample scripts and documentation remains with you. In no event shall
' Microsoft, its authors, or anyone else involved in the creation, production, or
' delivery of the scripts be liable for any damages whatsoever (including,
' without limitation, damages for loss of business profits, business interruption,
' loss of business information, or other pecuniary loss) arising out of the use
' of or inability to use the sample scripts or documentation, even if Microsoft
' has been advised of the possibility of such damages.
'---------------------------------------------------------------------------------
Option Explicit
' ################################################
' The starting point of execution for this script.
' ################################################
Sub Main()
	Dim wsArgNum
	' Get the number of parameters from command-line.
	wsArgNum = WScript.Arguments.Count
	Dim strFullPaths,strFullPath,FilePath,FileName
	Dim objShell,objFolder,objFolderItem,colVerbs,objFSO
	Set objFSO = CreateObject("Scripting.FileSystemObject")
	
	Dim flag,i
	Select Case wsArgNum
		Case 0 
			Wscript.Echo "Please drag at least one file onto this VBScript file."
		Case Else 
			For i = 0 To  wsArgNum - 1
				strFullPath = WScript.Arguments(i)
				FilePath = objFSO.GetFolder(GetNameSpace(strFullPath))	'Get the base path of file
				FileName = GetFileName(strFullPath)		'Get the file name	
				flag = 0
				Set objShell = CreateObject("Shell.Application")  
				Set objFolder = objShell.Namespace(FilePath)
				Set objFolderItem = objFolder.ParseName(FileName) 
				Set colVerbs = objFolderItem.Verbs 
				Dim objVerb
				For Each objVerb in colVerbs			'Verify the file can be pinned to start menu
					If Replace(objVerb.name, "&", "") = "Pin to Start" Then 
					objVerb.DoIt
					Flag = 1
					End If
				Next
				If flag = 1 Then 
					msgbox "Adding the item "&FileName&" to start menu done!"
				ElseIf flag = 0 Then 
					msgbox "This type of file "&FileName&" can not be pinned to start menu!"
				End If 
			Next 
	End Select 	
End Sub 

' #########################################
' Get base path of the file
' #########################################
Function GetNameSpace(FullPath)
	Dim Position	' Path separator.
	GetNameSpace = ""
	Position = InStrRev(FullPath, "\", -1, 1)
	If Position <> 0 Then GetNameSpace = Left(FullPath, Position)
End Function

' #########################################
' Get file name 
' #########################################
Function GetFileName(FullPath)
	Dim Position	' Path separator.
	Dim lngDotPosition				' Dot position.
	Dim strFile						' A full file name.
	GetFileName = ""
	Position = InStrRev(FullPath, "\", -1, 1)
	If Position <> 0 Then
		GetFileName = Right(FullPath, Len(FullPath) - Position)	
	End If
End Function

Call Main