# Mundo-Daily-Journal: 期刊学习 — 每日 6:00
$action = New-ScheduledTaskAction `
  -Execute 'E:\Git\usr\bin\bash.exe' `
  -Argument '-l -c "cd ~/Desktop/love-dandan && bash mundo-cloud/scripts/daily_journal.sh >> ~/Desktop/love-dandan/logs/daily_journal_$(date +%Y%m%d).log 2>&1"' `
  -WorkingDirectory 'C:\Users\25176\Desktop\love-dandan'

$trigger = New-ScheduledTaskTrigger -Daily -At 6am

$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -StartWhenAvailable `
  -MultipleInstances IgnoreNew

Register-ScheduledTask `
  -TaskName 'Mundo-Daily-Journal' `
  -Action $action `
  -Trigger $trigger `
  -Settings $settings `
  -Description 'Mundo journal learning — Nature/Science/Cell RSS daily 6am' `
  -Force

Write-Host "Mundo-Daily-Journal registered OK"
