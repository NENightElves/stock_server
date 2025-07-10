import flask
from flask import request
import waitress
import stock_util

app = flask.Flask(__name__)


@app.route('/api/stock')
def stock():
    stock_code = request.args.get('code')
    ret_data = stock_util.calc_stock_metrics(stock_util.get_stock_data_by_days(stock_code)).to_dict('records')
    return {"msg": "success", "data": ret_data}


if __name__ == '__main__':
    waitress.serve(app, port=5000)
