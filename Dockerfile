FROM python:3.12

WORKDIR /app
RUN git clone https://github.com/NENightElves/stock_server.git
RUN pip install akshare flask flask_cors waitress

EXPOSE 5000
WORKDIR /app/stock_server/src
CMD ["python", "main.py"]
