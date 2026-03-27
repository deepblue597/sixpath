@echo off
setlocal

echo === Sixpath Setup ===

:: Check if Docker is installed
where docker >nul 2>nul
if %errorlevel% equ 0 (
    echo Docker is already installed.
    docker --version
) else (
    echo Docker not found. Installing Docker Desktop...
    echo.
    echo Downloading Docker Desktop installer...
    powershell -Command "Invoke-WebRequest -Uri 'https://desktop.docker.com/win/main/amd64/Docker%%20Desktop%%20Installer.exe' -OutFile '%TEMP%\DockerDesktopInstaller.exe'"
    echo Running Docker Desktop installer...
    start /wait "" "%TEMP%\DockerDesktopInstaller.exe" install --quiet
    del "%TEMP%\DockerDesktopInstaller.exe"
    echo.
    echo Docker Desktop installed. Please restart your computer, then run this script again.
    pause
    exit /b 1
)

:: Verify Docker is running
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo Docker is installed but not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

:: Check if docker compose is available
docker compose version >nul 2>nul
if %errorlevel% neq 0 (
    echo Docker Compose not found. Please update Docker Desktop.
    pause
    exit /b 1
)

:: Check for .env file
if not exist .env (
    echo Warning: No .env file found. The app requires environment variables to run.
    echo Please create a .env file before proceeding.
    pause
    exit /b 1
)

:: Run the application
echo Starting Sixpath application...
docker compose up -d

echo.
echo === Sixpath is running! ===
echo Frontend: http://localhost:3001
echo Backend:  http://localhost:8000
echo Database: localhost:5432
echo.
pause
