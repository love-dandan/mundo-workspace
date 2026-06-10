@echo off
REM ============================================================
REM 蒙多云端进化 — 每日 3:00 自动同步
REM 由 Windows Task Scheduler 触发
REM ============================================================
setlocal

REM 切换到项目目录
cd /d %USERPROFILE%\Desktop\love-dandan

REM 确保 Git Bash 和 Git 在 PATH 中
set "PATH=E:\Git\usr\bin;E:\Git\mingw64\bin;%PATH%"
set "HOME=%USERPROFILE%"

REM 获取日志日期戳
for /f "tokens=2 delims==" %%I in ('"wmic os get localdatetime /value"') do set "DT=%%I"
set "LOGDATE=%DT:~0,4%%DT:~4,2%%DT:~6,2%"

REM 执行每日进化
bash mundo-cloud/scripts/daily_evolve.sh >> logs\daily_evolve_%LOGDATE%.log 2>&1

endlocal
