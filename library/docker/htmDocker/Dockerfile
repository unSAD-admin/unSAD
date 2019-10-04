FROM ubuntu:latest

RUN echo "Building a docker image!"

RUN echo "Starting an Ubuntu image and running updates"
RUN apt-get update
RUN apt-get -y upgrade


RUN echo "Installing pip for python2"
RUN apt-get install --assume-yes python-pip

RUN echo "Installing python2 libraries"

RUN pip2 install nupic Flask


COPY /htmHome/* /home/htmHome/

RUN python /home/htmHome/detector_service_provider.py

