FROM python:3.7

# Main application setup
WORKDIR /application

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

VOLUME ./save_folder

ENTRYPOINT ["./docker-entrypoint.sh"]