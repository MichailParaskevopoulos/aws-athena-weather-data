FROM python:3.8-slim-buster

ARG ACCESS_KEY
ARG SECRET_KEY

ENV ACCESS_KEY=$ACCESS_KEY
ENV SECRET_KEY=$SECRET_KEY

WORKDIR /src

COPY src/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "src/main.py"]