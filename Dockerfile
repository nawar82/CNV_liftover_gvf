FROM python:3.10.6-slim-buster

COPY api api
COPY research_topics_ranker research_topics_ranker
COPY notebooks notebooks
COPY setup.py setup.py
COPY __init__.py __init__.py
COPY Makefile Makefile
COPY .envrc .envrc
COPY requirements.txt requirements.txt
COPY .gitignore .gitignore


RUN pip install -r requirements.txt
RUN pip install -e .

# For local
#CMD uvicorn api.fast:app --host 0.0.0.0
# For deployment
CMD uvicorn api.fast:app --host 0.0.0.0  --port $PORT
