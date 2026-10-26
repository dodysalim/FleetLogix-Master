@echo off
REM ================================================================
REM FleetLogix · Quick Fix (doble-clic)
REM Ejecuta dim_date + 8 vistas en tu PostgreSQL local
REM ================================================================

cd /d "%~dp0..\.."
echo.
echo Ejecutando FleetLogix Quick Fix desde:
echo   %cd%
echo.
python dashboard\setup\quick_fix.py
echo.
pause
