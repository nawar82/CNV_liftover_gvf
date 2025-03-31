# syntax=docker/dockerfile:1    ## While optional, this directive instructs the Docker builder what syntax to use when parsing the Dockerfile
                                ## We recommend using docker/dockerfile:1, which always points to the latest release of the version 1 syntax.
                                ## BuildKit automatically checks for updates of the syntax before building, making sure you are using the most current version.

FROM python:3.10.6-slim-buster

RUN apt-get update && apt-get install -y libc6  # libc6 is the package name for the GNU C Library (glibc) in Debian-based systems (like Ubuntu)
                                                # This is because the apptainer image (singularity also) doesn't work well with liftover without this package
# Set the working directory inside the container
#WORKDIR /app

COPY results results
COPY scripts/liftover_and_gvf_MultipleFIles.py scripts/liftover_and_gvf_MultipleFIles.py
COPY scripts/helper scripts/helper
COPY scripts/__init__.py scripts/__init__.py

COPY __init__.py __init__.py
COPY .envrc .envrc
COPY .env .env
COPY requirements.txt requirements.txt
COPY .gitignore .gitignore
#COPY test_data/file_list.txt test_data/file_list.txt
#COPY test_data/input.vcf test_data/input.vcf
#COPY test_data/input2.vcf test_data/input2.vcf

RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install -e .

# Set the entrypoint to Python so users can run the script easily
ENTRYPOINT ["python", "./scripts/liftover_and_gvf_MultipleFIles.py"]
