FROM ubuntu:20.04
WORKDIR /jjw
RUN apt update && apt install -y python3-pip
COPY . .
RUN pip install .
ENTRYPOINT ["jjwrecker"]
CMD ["--help"]
