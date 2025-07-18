FROM node:lts AS node
RUN cd / && git clone https://github.com/NENightElves/stock_server.git && \
    cd stock_server && sh build.sh


FROM python:3.12
COPY --from=node /stock_server/src /app/server
COPY --from=node /stock_server/requirements.txt /app
RUN cd /app && pip install -r requirements.txt

EXPOSE 5000
WORKDIR /app/server
CMD ["python", "-m", "waitress", "main:app"]
