FROM python:3.12

WORKDIR /var/run

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 6002

RUN touch nonce.txt

COPY 4.txt cbc.html encryptle_cbc.py ./

CMD ["flask", "--app", "encryptle_cbc", "run", "--port", "6002", "--host", "0.0.0.0"]
