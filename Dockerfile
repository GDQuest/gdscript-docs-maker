FROM docker.io/barichello/godot-ci:latest


COPY . /app

RUN apt update && apt -y install python3 python3-setuptools

WORKDIR /app

RUN python3 setup.py install

ENTRYPOINT ["./generate_reference"]
