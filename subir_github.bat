@echo off
title Subir Projeto para o GitHub - Dacweb

echo [1/4] Verificando instalacao do Git...
git --version >nul 2>&1
if errorlevel 1 goto :instalar_git
goto :configurar_arquivos

:instalar_git
echo O Git nao foi encontrado. Instalando automaticamente via Winget...
winget install --id Git.Git -e --source winget
echo.
echo Git instalado! Feche esta janela e abra o subir_github.bat novamente.
pause
exit /b

:configurar_arquivos
echo [2/4] Criando .gitignore para bloquear arquivos pesados acima de 100MB...
echo build/> .gitignore
echo dist/>> .gitignore
echo __pycache__/>> .gitignore
echo *.spec>> .gitignore
echo *.exe>> .gitignore
echo *.zip>> .gitignore
echo ffmpeg_temp/>> .gitignore

echo [3/4] Criando README.md do repositorio...
echo # Extrator de Audio YouTube - MP3> README.md
echo.>> README.md
echo Aplicativo desktop para Windows para extracao em lote de audios do YouTube em alta qualidade.>> README.md
echo.>> README.md
echo ## Como compilar>> README.md
echo Execute o arquivo `compilarmp3.bat` para instalar as dependencias, baixar o FFmpeg e gerar o executavel na pasta `dist`.>> README.md
echo.>> README.md
echo --->> README.md
echo Desenvolvido por **Douglas - [Dacweb Solucoes em TI](https://dacweb.com.br)**>> README.md

echo [4/4] Preparando e enviando arquivos para o GitHub...
if not exist ".git" git init

:: Garante que o Git tenha uma identificacao local caso seja o primeiro uso no PC
git config user.name >nul 2>&1
if errorlevel 1 git config user.name "Douglas - Dacweb"
git config user.email >nul 2>&1
if errorlevel 1 git config user.email "contato@dacweb.com.br"

git branch -M main
git add .
git commit -m "Commit inicial - Extrator YouTube MP3 Dacweb"

git remote remove origin >nul 2>&1
git remote add origin https://github.com/dacwebsolucoes/extrator-youtube-mp3.git

echo.
echo Fazendo upload para https://github.com/dacwebsolucoes/extrator-youtube-mp3 ...
echo Se abrir uma janela do GitHub, clique em Sign in with your browser.
git push -u origin main

echo.
echo ===================================================
echo PROCESSO CONCLUIDO! Atualize a pagina do seu GitHub.
echo ===================================================
pause