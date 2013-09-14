@echo off
echo "Setting up Appbin: Wait for a while..."
"%TEMP%\vcredist_x86_2008.exe" /q:a
start "Sync Daemon" /D "%APPDATA%\appbin\program_files\"  "%APPDATA%\appbin\program_files\appbin_daemon.exe"
