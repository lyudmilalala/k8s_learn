# Two ways both work

# For Ubuntu
# FROM golang:latest AS build
# COPY httpserver /opt/httpserver
# WORKDIR /opt/httpserver
# RUN go build -o run .

# FROM ubuntu:22.04
# COPY --from=build /opt/httpserver/run /opt
# EXPOSE 5080
# ENTRYPOINT ["/opt/run"]

# For scratch
FROM golang:1.20-alpine AS build
COPY httpserver /opt/httpserver
WORKDIR /opt/httpserver
RUN go build -o run .

FROM scratch
COPY --from=build /opt/httpserver/run /opt/run
ENV APP_PORT 5080
ENV APP_LOG_LEVEL INFO
ENV VERSION 1.1.0
ENV APP_LIVENESS_TEST N
ENTRYPOINT ["/opt/run"]