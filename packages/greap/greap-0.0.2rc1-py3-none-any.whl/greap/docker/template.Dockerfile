FROM python:3.9-slim

RUN apt-get clean && apt-get update && apt-get install -y git && apt-get install -y libmariadb-dev && apt-get install -y gcc

WORKDIR greap

ADD . /greap

RUN python -m pip install git+https://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@github.com/greaphello/greap.git

# Install your dependencies here
# RUN pip install -r requirements.txt
RUN pip install -r requirements.txt

ENV BACKTEST_DATA_PATH=/greap/backtest.db

ENTRYPOINT ["greap"]
