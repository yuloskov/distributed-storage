FROM python:3.7-alpine

# Main application setup
WORKDIR /application


COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY ./main.py .

CMD python3 main.py

