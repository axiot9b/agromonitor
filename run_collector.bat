@echo off
REM AgroMonitor Data Collector - Windows Task Scheduler
REM Este script cambia al directorio correcto antes de ejecutar

cd /d "C:\Users\EfrainTorres\Documents\agro proyect"
python agro_data_collector.py

echo [%date% %time%] Ejecucion completada >> logs\task_scheduler.log
