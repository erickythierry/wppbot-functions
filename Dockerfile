FROM python
RUN mkdir app
WORKDIR /app
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y
RUN apt install ffmpeg tzdata -y
ENV TZ="America/Belem"
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "wsgi.py"]