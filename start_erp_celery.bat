@echo off
cd /d "E:\production\erp\erp_master"
call "E:\production\erp\venv\Scripts\activate.bat"

REM Start worker in background (no new window)
start /b "" cmd /c "celery -A erp_master worker --pool=solo -l info -Q erp_master_queue >> logs\celery_worker.log 2>&1"

REM Start beat in background (no new window)
start /b "" cmd /c "celery -A erp_master beat -l info >> logs\celery_beat.log 2>&1"
