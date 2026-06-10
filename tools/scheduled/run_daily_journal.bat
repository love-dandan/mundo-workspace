@echo off
REM ============================================================
REM 蒙多期刊学习 — 每日 6:00 自动抓取 Nature/Science/Cell
REM 由 Windows Task Scheduler 触发
REM ============================================================
setlocal

REM 切换到项目目录
cd /d %USERPROFILE%\Desktop\love-dandan

REM 确保 Git Bash 和 Git 在 PATH 中
set "PATH=E:\Git\usr\bin;E:\Git\mingw64\bin;C:\Users\25176\AppData\Local\Programs\Python\Python311;%PATH%"
set "HOME=%USERPROFILE%"

REM 获取日志日期戳
for /f "tokens=2 delims==" %%I in ('"wmic os get localdatetime /value"') do set "DT=%%I"
set "LOGDATE=%DT:~0,4%%DT:~4,2%%DT:~6,2%"

REM 执行每日期刊学习
bash mundo-cloud/scripts/daily_journal.sh >> logs\daily_journal_%LOGDATE%.log 2>&1

endlocal
