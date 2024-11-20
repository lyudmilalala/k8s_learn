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
EXPOSE 5080
ENTRYPOINT ["/opt/run"]