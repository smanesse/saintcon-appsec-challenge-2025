FROM python:3.12

WORKDIR /var/run

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 6001

RUN touch nonce.txt

COPY 6.txt ecb.html encryptle_ecb.py ./

CMD ["flask", "--app", "encryptle_ecb", "run", "--port", "6001", "--host", "0.0.0.0"]
