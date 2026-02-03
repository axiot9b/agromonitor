# AgroMonitor Data Collector - PowerShell Script
# Este script es llamado por Task Scheduler

$projectPath = "C:\Users\EfrainTorres\Documents\agro proyect"
$logPath = Join-Path $projectPath "logs"
$logFile = Join-Path $logPath "task_scheduler.log"

# Crear directorio de logs si no existe
if (!(Test-Path $logPath)) {
    New-Item -ItemType Directory -Path $logPath -Force | Out-Null
}

# Registrar inicio
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $logFile -Value "[$timestamp] Iniciando recoleccion..."

# Cambiar al directorio del proyecto
Set-Location $projectPath

# Ejecutar el script Python
try {
    python agro_data_collector.py
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "[$timestamp] Recoleccion completada exitosamente"
} catch {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "[$timestamp] ERROR: $($_.Exception.Message)"
}
