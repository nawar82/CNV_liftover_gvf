FROM python:3.8.12-slim

COPY requirements.txt requirements.txt
COPY scripts scripts
COPY setup.py setup.py

RUN pip install -e .

# For local
#CMD uvicorn package_folder.api_file:app --host 0.0.0.0
# For deployment
#CMD uvicorn package_folder.api_file:app --host 0.0.0.0  --port $PORT
