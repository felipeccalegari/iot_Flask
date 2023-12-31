FROM python:3


WORKDIR /usr/src/app
ENV FLASK_APP = app.py
ENV FLASK_RUN_HOST = 0.0.0.0

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python3", "app.py" ]