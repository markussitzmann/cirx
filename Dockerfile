ARG build_tag
FROM cactvs-django-app-server:$build_tag
ARG conda_py

LABEL maintainer="markus.sitzmann@gmail.com "

ENV PATH /opt/conda/bin:$PATH

RUN apt update && \
  apt -y upgrade && \
  apt install -y postgresql-client

COPY requirements.txt /

RUN /bin/bash -c "source activate cactvs" && \
    CONDA_PY=$conda_py pip install -r /requirements.txt

