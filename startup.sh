#!/bin/bash
set -e

echo "=========================================="
echo "Starting MoI Reporting API"
echo "=========================================="

cd /home/site/wwwroot

echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Verifying package installations..."
python -c "import uvicorn; print('✓ uvicorn:', uvicorn.__version__)"
python -c "import gunicorn; print('✓ gunicorn:', gunicorn.__version__)"
python -c "import fastapi; print('✓ fastapi:', fastapi.__version__)"
python -c "import sqlalchemy; print('✓ sqlalchemy:', sqlalchemy.__version__)"

echo "Starting Gunicorn with Uvicorn workers..."
exec gunicorn app.main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile -