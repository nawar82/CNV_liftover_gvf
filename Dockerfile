FROM python:3.10.6-slim

COPY requirements.txt requirements.txt
COPY scripts scripts
COPY setup.py setup.py

RUN pip install --no-cache-dir -r requirements.txt


#CMD [ "python", "./scripts/liftover_and_gvf_MultipleFIles.py -i ./test_data/file_list.txt" ]
