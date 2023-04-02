FROM python:3.8-slim-buster

ENV ACCESS_KEY=AKIATPOZRPAYOOSG3XH5
ENV SECRET_KEY=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

WORKDIR /src

COPY src/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "src/main.py"]