FROM ubuntu:20.04
#RUN apt-get update && apt-get install -y git
#RUN git clone -b master https://github.com/google/or-tools

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3-pip

RUN pip3 install -U pip
RUN pip3 install flask ortools
RUN mkdir /app
WORKDIR /app


COPY ./app /app

EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["tsm.py"]