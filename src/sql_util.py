import sqlalchemy
from sqlalchemy import text
import pandas as pd
import datetime
import json
import os


def init_db(drop=False):
    if drop:
        with sql_engine.begin() as conn:
            conn.execute(text('DROP TABLE IF EXISTS stocks'))
            conn.execute(text('DROP TABLE IF EXISTS stock_cache_log'))
    sql1 = '''
        CREATE TABLE IF NOT EXISTS stocks (
            symbol TEXT NOT NULL,
            date DATE NOT NULL,
            open REAL NOT NULL,
            close REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            volume INTEGER NOT NULL,
            turnover REAL NOT NULL,
            amplitude REAL NOT NULL,
            change_pct REAL NOT NULL,
            change_amt REAL NOT NULL,
            turnover_rate REAL NOT NULL,
            ma5 REAL,
            ma10 REAL,
            ma20 REAL,
            rsi REAL,
            macd REAL,
            macd_signal REAL,
            macd_hist REAL,
            bb_upper REAL,
            bb_middle REAL,
            bb_lower REAL,
            kdj_k REAL,
            kdj_d REAL,
            kdj_j REAL,
            volume_ma20 REAL,
            volume_ratio20 REAL,
            atr REAL,
            volatility REAL,
            roc REAL,
            PRIMARY KEY (symbol, date)
        )
    '''
    sql2 = 'CREATE INDEX symbol_date_idx ON stocks (symbol, date)'
    sql3 = '''
        CREATE TABLE IF NOT EXISTS stock_cache_log(
            symbol TEXT NOT NULL,
            log TEXT NOT NULL
        )
    '''
    with sql_engine.begin() as conn:
        conn.execute(text(sql1))
        conn.execute(text(sql2))
        conn.execute(text(sql3))


def insert_stock_data(df: pd.DataFrame):
    with sql_engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(text('DELETE FROM stocks WHERE symbol=:symbol AND date=:date'),
                         {'symbol': row['symbol'], 'date': row['date']})
    df.to_sql('stocks', sql_engine, if_exists='append', index=False)


def set_update_date(stock_code, start_date, end_date):
    with sql_engine.begin() as conn:
        r = conn.execute(text('SELECT * FROM stock_cache_log WHERE symbol=:symbol'), {'symbol': stock_code})
        x = r.fetchone()
        if x is None:
            if '-' not in start_date:
                start_date = datetime.datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
                end_date = datetime.datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
            conn.execute(text('INSERT INTO stock_cache_log (symbol, log) VALUES (:symbol, :log)'),
                         {'symbol': stock_code, 'log': json.dumps([{'start_date': start_date, 'end_date': end_date}])})
        else:
            j = json.loads(x[1])
            ds = []
            for i in j:
                d1 = datetime.datetime.strptime(i['start_date'], '%Y-%m-%d')
                d2 = datetime.datetime.strptime(i['end_date'], '%Y-%m-%d')
                ds.append((d1, d2))
            if '-' in start_date:
                ds.append((datetime.datetime.strptime(start_date, '%Y-%m-%d'), datetime.datetime.strptime(end_date, '%Y-%m-%d')))
            else:
                ds.append((datetime.datetime.strptime(start_date, '%Y%m%d'), datetime.datetime.strptime(end_date, '%Y%m%d')))
            ds.sort(key=lambda x: x[0])
            mds = [ds[0]]
            for curr in ds[1:]:
                last = mds[-1]
                if curr[0] <= last[1]:
                    mds[-1] = (last[0], max(last[1], curr[1]))
                else:
                    mds.append(curr)
            mdss = []
            for i in mds:
                mdss.append({'start_date': i[0].strftime('%Y-%m-%d'), 'end_date': i[1].strftime('%Y-%m-%d')})
            conn.execute(text('UPDATE stock_cache_log SET log=:log WHERE symbol=:symbol'),
                         {'symbol': stock_code, 'log': json.dumps(mdss)})


def get_stock_data_by_days(stock_code, last_date, number=30):
    with sql_engine.connect() as conn:
        df = pd.read_sql_query('SELECT * FROM (SELECT * FROM stocks WHERE symbol=:symbol AND date<=:last_date ORDER BY date DESC LIMIT :number) ORDER BY date', conn,
                               params={'symbol': stock_code, 'last_date': last_date, 'number': number})
        df['date'] = df['date'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
        return df


def get_stock_data_by_date(stock_code, start_date, end_date):
    if '-' not in start_date:
        start_date = datetime.datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
    if '-' not in end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
    with sql_engine.connect() as conn:
        df = pd.read_sql_query('SELECT * FROM stocks WHERE symbol=:symbol AND date>=:start_date AND date<=:end_date ORDER BY date', conn,
                               params={'symbol': stock_code, 'start_date': start_date, 'end_date': end_date})
        df['date'] = df['date'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
        return df


def get_update_date(stock_code):
    with sql_engine.connect() as conn:
        r = conn.execute(text('SELECT * FROM stock_cache_log WHERE symbol=:symbol'), {'symbol': stock_code})
        x = r.fetchone()
        if x is None:
            return None
        else:
            return json.loads(x[1])


def check_in_cache(stock_code, start_date, end_date):
    with sql_engine.connect() as conn:
        r = conn.execute(text('SELECT * FROM stock_cache_log WHERE symbol=:symbol'), {'symbol': stock_code})
        x = r.fetchone()
        if x is None:
            return False
        j = json.loads(x[1])
        ds = []
        for i in j:
            d1 = datetime.datetime.strptime(i['start_date'], '%Y-%m-%d')
            d2 = datetime.datetime.strptime(i['end_date'], '%Y-%m-%d')
            ds.append((d1, d2))
        if '-' in start_date:
            sd = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            ed = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        else:
            sd = datetime.datetime.strptime(start_date, '%Y%m%d')
            ed = datetime.datetime.strptime(end_date, '%Y%m%d')
        for i in ds:
            if sd >= i[0] and ed <= i[1]:
                return True
        return False


if not os.path.exists('stock.db'):
    sql_engine = sqlalchemy.create_engine('sqlite:///stock.db')
    init_db()
sql_engine = sqlalchemy.create_engine('sqlite:///stock.db')
