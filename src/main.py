import os
import flask
import flask_cors
import init_env
import logging
from flask import request, Response, send_file
import stock.stock_util as stock_util
import llm.llm_util as llm_util
import llm.prompt_util as prompt_util

logging.basicConfig(level=logging.INFO)
if os.path.exists('static'):
    app = flask.Flask(__name__, static_folder='static', static_url_path='')
else:
    app = flask.Flask(__name__)
flask_cors.CORS(app)


@app.route('/')
def index():
    if os.path.exists('static'):
        return send_file('./static/index.html')
    else:
        return 'Stock Server'


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


@app.route('/api/stock_analyse', methods=['POST'])
def stock_analyse():
    j = request.json
    stock_code = j['code']
    stock_data = None
    if 'days' in j:
        days = int(j['days'])
        if 'end_date' in j:
            end_date = j['end_date']
            stock_data = stock_util.get_stock_data_by_days(stock_code, days=days, end_date=end_date)
        else:
            stock_data = stock_util.get_stock_data_by_days(stock_code, days=days)
    elif 'start_date' in j and 'end_date' in j:
        start_date = j['start_date']
        end_date = j['end_date']
        stock_data = stock_util.get_stock_data_by_date(stock_code, start_date, end_date)
    else:
        stock_data = stock_util.get_stock_data_by_days(stock_code)
    df = stock_util.calc_stock_metrics(stock_data)
    df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    ret_data = df.to_dict('records')
    headers = {
        'Cache-Control': 'no-cache'
    }
    vendor = 'dashscope'
    if 'llm' in j:
        if j['llm'] == 'deepseek':
            vendor = 'deepseek'
            if 'llm_model' in j:
                llm = llm_util.get_llm_deepseek(model=j['llm_model'])
            else:
                llm = llm_util.get_llm_deepseek()
    else:
        if 'llm_model' in j:
            llm = llm_util.get_llm_tongyi(model=j['llm_model'])
        else:
            llm = llm_util.get_llm_tongyi()

    def make_response():
        for chunk in prompt_util.prompt_once_stock(llm, stock_code, ret_data, stream=True):
            if vendor == 'deepseek':
                yield chunk.content
            else:
                yield chunk
    return Response(make_response(), mimetype='text/event-stream', headers=headers)


if __name__ == '__main__':
    app.run(debug=True)
