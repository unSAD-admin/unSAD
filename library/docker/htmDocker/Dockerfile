# Follow the following step to build image and start the service
# start you docker d
# docker build -t htm/htm:1.0 .
# docker run -p 127.0.0.1:8081:8081 -it [image id]
# nohup python /home/htmHome/detector_service_provider.py


FROM ubuntu:latest

RUN echo "Building a docker image!"

RUN echo "Starting an Ubuntu image and running updates"
RUN apt-get update
RUN apt-get -y upgrade


RUN echo "Installing pip for python2"
RUN apt-get install --assume-yes python-pip

RUN echo "Installing python2 libraries"

RUN pip2 install nupic
RUN pip2 install Flask


COPY /htmHome/* /home/htmHome/

EXPOSE 8081:8081

