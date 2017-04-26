FROM python:3.6
ENV PYTHONUNBUFFERED 1
ENV API_HOST api
ENV API_PORT 80
WORKDIR /opt/equaliser-web
COPY . /opt/equaliser-web
RUN pip3 install .
EXPOSE 80
CMD . bin/docker_entrypoint
