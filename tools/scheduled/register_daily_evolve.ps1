# Mundo-Daily-Evolve: 云端进化 — 每日 3:00
$action = New-ScheduledTaskAction `
  -Execute 'E:\Git\usr\bin\bash.exe' `
  -Argument '-l -c "cd ~/Desktop/love-dandan && bash mundo-cloud/scripts/daily_evolve.sh >> ~/Desktop/love-dandan/logs/daily_evolve_$(date +%Y%m%d).log 2>&1"' `
  -WorkingDirectory 'C:\Users\25176\Desktop\love-dandan'

$trigger = New-ScheduledTaskTrigger -Daily -At 3am

$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -StartWhenAvailable `
  -MultipleInstances IgnoreNew

Register-ScheduledTask `
  -TaskName 'Mundo-Daily-Evolve' `
  -Action $action `
  -Trigger $trigger `
  -Settings $settings `
  -Description 'Mundo cloud sync evolution — daily 3am' `
  -Force

Write-Host "Mundo-Daily-Evolve registered OK"
