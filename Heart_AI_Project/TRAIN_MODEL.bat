@echo off
cd /d "%~dp0"
echo Training CardioRisk AI on 4 merged UCI datasets...
python -m pip install -r requirements.txt -q
python train_model.py
echo.
echo Done. Metrics saved to model_metrics.json
pause
