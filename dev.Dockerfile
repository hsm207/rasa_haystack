FROM rasa/rasa-sdk:2.8.2

USER root
RUN apt update && \
    apt install -y git \
        make \
        poppler-utils \
        wget 

RUN pip install --no-cache-dir black \
    farm-haystack[ocr]==1.3.0 \
    debugpy \
    jupyterlab \
    pytest \
    wikipedia