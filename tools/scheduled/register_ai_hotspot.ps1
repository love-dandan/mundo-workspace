# Mundo-AI-Hotspot: AI热点日报 — 每日 7:00
$action = New-ScheduledTaskAction `
  -Execute 'C:\Users\25176\AppData\Local\Programs\Python\Python311\python.exe' `
  -Argument 'tools/ai-hotspot-crawler.py' `
  -WorkingDirectory 'C:\Users\25176\Desktop\love-dandan'

$trigger = New-ScheduledTaskTrigger -Daily -At 7am

$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -StartWhenAvailable `
  -MultipleInstances IgnoreNew

Register-ScheduledTask `
  -TaskName 'Mundo-AI-Hotspot' `
  -Action $action `
  -Trigger $trigger `
  -Settings $settings `
  -Description 'Mundo AI hotspot daily — crawl aihot.virxact.com, save JSON, commit push' `
  -Force

Write-Host "Mundo-AI-Hotspot registered OK"
