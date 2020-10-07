FROM python:3.7

WORKDIR /application

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY ./api.py .
COPY ./client.py .

COPY ./cli.sh /root/.bashrc

#ENTRYPOINT ["python3", "-u", "client.py"]
#CMD ["init", "./dfs", "-f", "-r"]
ENTRYPOINT ["/bin/bash"]
