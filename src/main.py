import flask
import flask_cors
from flask import request
import waitress
import stock_util
import logging

app = flask.Flask(__name__)
flask_cors.CORS(app)


@app.route('/api/stock')
def stock():
    stock_code = request.args.get('code')
    stock_data = None
    if request.args.get('days'):
        days = int(request.args.get('days'))
        if request.args.get('end_date'):
            end_date = request.args.get('end_date')
            stock_data = stock_util.get_stock_data_by_days(stock_code, days=days, end_date=end_date)
        else:
            stock_data = stock_util.get_stock_data_by_days(stock_code, days=days)
    elif request.args.get('start_date') and request.args.get('end_date'):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        stock_data = stock_util.get_stock_data(stock_code, start_date, end_date)
    else:
        stock_data = stock_util.get_stock_data_by_days(stock_code)
    df = stock_util.calc_stock_metrics(stock_data)
    df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    ret_data = df.to_dict('records')
    return {"msg": "success", "data": ret_data}


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    waitress.serve(app, port=5000)
