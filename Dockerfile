FROM python:3.7.5-slim
WORKDIR /home/max/python
COPY lab1.py .
CMD ["python", "lab1.py"]
