Some detector may be implemented with docker. This directory is used to store all the related docker file


# How to start the docker environment for HTM detector

On most of the linux machine with docker and python docker API installed, you don't need to start the docker environment
manually. The library will start the docker environment by itself. You just need to provide the path to the Dockerfile
when initialize your htm detector

    detector = HTMAnomalyDetector()
    detector.initalize(docker_path = "path/to/your/Dockerfile/directory")

What the library will try to do is: create a new docker image based on the dockerfile under the provided directory
start a container using that image and start a flask server listening the port 8081 (you can control the port
number using port parameter) on your local machine. The docker environment will not be recycled even after the program
finished.

But there are situations where the library can't or don't need to create the docker environment. Creating a docker
environment can be expensive. You may want to reuse the docker environment. So the suggested way is to launch the 
docker environment manually

    # start you docker and direct to the directory container Dockerfile: then 
    docker build -t htm/htm:1.0 .
    docker run -p 127.0.0.1:8081:8081 -it [image id]
    nohup python /home/htmHome/detector_service_provider.py
    
    # leave your terminal there and do not close it so as to keep the process alive
    
Now, a docker environment is setup and you need to tell the Htm detector how to access to it instead of trying to 
create a new one:

    detector.initalize(docker_ip="127.0.0.1",port=8081)
    # By the way, by default the detector will check whether the 127.0.0.1 address is usable, so you actually don't
    # need to pass in the parameter, it is the same as
    detector.initalize()
    
It is possible that the docker process is running on another machine other than your local machine, in that case you can specify
you ip address and port number:

    detector.initalize(docker_ip="65.56.59.22",port=6069)
    

    