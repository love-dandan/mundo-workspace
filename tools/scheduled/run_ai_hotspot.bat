@echo off
REM ============================================================
REM 蒙多AI热点日报 — 每日 7:00 自动抓取
REM 由 Windows Task Scheduler 触发
REM ============================================================
setlocal

REM 切换到项目目录
cd /d %USERPROFILE%\Desktop\love-dandan

REM 确保 Git 在 PATH 中
set "PATH=E:\Git\mingw64\bin;%PATH%"
set "HOME=%USERPROFILE%"

REM 获取日志日期戳
for /f "tokens=2 delims==" %%I in ('"wmic os get localdatetime /value"') do set "DT=%%I"
set "LOGDATE=%DT:~0,4%%DT:~4,2%%DT:~6,2%"
set "LOG=logs\ai_hotspot_%LOGDATE%.log"

REM 配置 Git 用户信息（Task Scheduler 环境变量不全）
git config user.email "mundo@lihongwei-cn.github.io" 2>nul
git config user.name "Mundo Bot" 2>nul

REM 执行 AI 热点抓取
C:\Users\25176\AppData\Local\Programs\Python\Python311\python.exe tools\ai-hotspot-crawler.py >> %LOG% 2>&1

REM 检查是否成功，成功则 commit + push
if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] Crawl OK >> %LOG%
    git add docs/ai-hotspots/ >> %LOG% 2>&1
    if not errorlevel 1 (
        for /f "tokens=2 delims==" %%I in ('"wmic os get localdatetime /value"') do set "DT=%%I"
        set "DATE_STR=%%DT:~0,4%%-%%DT:~4,2%%-%%DT:~6,2%%"
        git commit -m "feat: 蒙多AI热点日报 %DATE_STR%" >> %LOG% 2>&1
        git push >> %LOG% 2>&1
    )
) else (
    echo [%date% %time%] Crawl FAILED with error %ERRORLEVEL% >> %LOG%
)

endlocal
