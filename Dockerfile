FROM python:3.12.14-trixie

WORKDIR /src

COPY requirements.txt requirements.txt
COPY build.sh build.sh

RUN pip install -r requirements.txt

COPY main.py main.py
COPY server.py server.py
COPY generate.py generate.py

COPY generator generator
COPY game game
COPY tests tests
COPY data data

EXPOSE 3000

# `main.py` dispatches to a subcommand.  Run the server by default; pass a
# different command to `docker run` to override it, e.g.
# `docker run <image> generator myworld --width 50`.
ENTRYPOINT [ "python3", "main.py" ]
CMD [ "server" ]
