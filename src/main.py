import flask
import flask_cors
import waitress
import init_env
import logging
from flask import request, Response
import stock.stock_util as stock_util
import llm.llm_util as llm_util
import llm.prompt_util as prompt_util

app = flask.Flask(__name__)
flask_cors.CORS(app)


@app.route('/api/stock_data')
def stock_data():
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
        stock_data = stock_util.get_stock_data_by_date(stock_code, start_date, end_date)
    else:
        stock_data = stock_util.get_stock_data_by_days(stock_code)
    df = stock_util.calc_stock_metrics(stock_data)
    df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    ret_data = df.to_dict('records')
    return {"msg": "success", "data": ret_data}


@app.route('/api/stock_analyse')
def stock_analyse():
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
        stock_data = stock_util.get_stock_data_by_date(stock_code, start_date, end_date)
    else:
        stock_data = stock_util.get_stock_data_by_days(stock_code)
    df = stock_util.calc_stock_metrics(stock_data)
    df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    ret_data = df.to_dict('records')
    llm = llm_util.get_llm_deepseek()

    def make_response():
        for chunk in prompt_util.prompt_once_stock(llm, stock_code, ret_data, stream=True):
            yield chunk.content
    return Response(make_response())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    waitress.serve(app, port=5000)
