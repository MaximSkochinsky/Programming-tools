FROM ubuntu
RUN apt update && apt install python3-pip -y
WORKDIR /home/max/python
COPY lab1.py .
RUN pip3 install pynput
CMD ["python3", "lab1.py"]
