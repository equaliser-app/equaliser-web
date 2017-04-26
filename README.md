# `equaliser-web`

This is the web client for generic browsers. It is powered by `equaliser-api`.

## Launch

There is little point in launching the website on its own, as it will not be able to produce a single page without the API present. Nevertheless, this service can be started with the following commands:

    docker build -t equaliser/web:1.0.0 .
    docker run -p 8081:80 equaliser/web:1.0.0
