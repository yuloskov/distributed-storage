FROM python:3.7

# Main application setup
WORKDIR /application

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY ./main.py .
COPY ./register.py .

VOLUME ./save_folder

CMD python3 -u main.py > flask.log

