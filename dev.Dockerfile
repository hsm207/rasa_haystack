FROM rasa/rasa-sdk:2.8.2

USER root
RUN apt update && \
    apt install -y git \
        make

RUN pip install --no-cache-dir black \
    farm-haystack==0.9.0 \
    debugpy \
    jupyterlab \
    pytest \
    wikipedia