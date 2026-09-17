FROM python:3.12.14-trixie

WORKDIR /src

COPY requirements.txt requirements.txt
COPY build.sh build.sh

RUN pip install -r requirements.txt

COPY main.py main.py

COPY generator generator
COPY game game
COPY tests tests
COPY data data

EXPOSE 3000

ENTRYPOINT [ "python3", "main.py" ]
