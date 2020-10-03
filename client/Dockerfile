FROM python:3.7

# Main application setup
WORKDIR /application

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY ./send_file.py .
COPY ./delete_file.py .

CMD sleep 10000


