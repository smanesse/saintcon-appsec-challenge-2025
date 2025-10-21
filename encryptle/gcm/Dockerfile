FROM python:3.12

WORKDIR /var/run

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 6003

RUN touch nonce.txt

COPY 5.txt gcm.html encryptle_gcm.py ./

CMD ["flask", "--app", "encryptle_gcm", "run", "--port", "6003", "--host", "0.0.0.0"]
