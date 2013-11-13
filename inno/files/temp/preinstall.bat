@echo off
echo "Preinstallation steps..."
taskkill /F /T /IM appbin_daemon.exe
taskkill /F /T /IM appbin_nw.exe
taskkill /F /T /IM appbin_7z.exe
