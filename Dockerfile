FROM python:3.12

WORKDIR /app
RUN git clone https://github.com/NENightElves/stock_server.git
RUN cd stock_server && pip install -r requirements.txt && sh build.sh

EXPOSE 5000
WORKDIR /app/stock_server/src
CMD ["python", "-m", "waitress", "main:app"]
