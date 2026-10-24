@echo off
title Compilador - Extrator MP3

echo [1/3] Bibliotecas verificadas!
py -m pip install customtkinter yt-dlp pyinstaller

if exist "ffmpeg.exe" goto :compilar

echo.
echo [2/3] Baixando FFmpeg - aguarde cerca de 80MB...
powershell -Command "Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'"

echo Extraindo ffmpeg.exe e ffprobe.exe...
powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'ffmpeg_temp' -Force"
for /r "ffmpeg_temp" %%f in (ffmpeg.exe ffprobe.exe) do if exist "%%f" copy "%%f" "." >nul
rmdir /s /q "ffmpeg_temp"
del "ffmpeg.zip"

:compilar
echo.
echo [3/3] Gerando o executavel na pasta dist...
py -m PyInstaller --noconfirm --onefile --windowed --name "ExtratorYouTubeMP3" --collect-all customtkinter --add-binary "ffmpeg.exe;." --add-binary "ffprobe.exe;." app.py

echo.
echo ===================================================
echo PRONTO! Seu programa esta em: C:\ExtratorMP3\dist
echo ===================================================
pause