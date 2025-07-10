import akshare as ak
import pandas as pd
import numpy as np
import datetime


def get_stock_data_by_days(stock_code, days=30):
    today = datetime.datetime.now()
    start_date = (today - datetime.timedelta(days=days)).strftime('%Y%m%d')
    end_date = today.strftime('%Y%m%d')
    stock_data = get_stock_data(stock_code, start_date, end_date)
    return stock_data


def get_stock_data(stock_code, start_date, end_date):
    column_map = {
        '日期': 'date',
        '股票代码': 'symbol',
        '开盘': 'open',
        '收盘': 'close',
        '最高': 'high',
        '最低': 'low',
        '成交量': 'volume',
        '成交额': 'turnover',
        '振幅': 'amplitude',
        '涨跌幅': 'change_pct',
        '涨跌额': 'change_amt',
        '换手率': 'turnover_rate'
    }
    stock_data = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date)
    stock_data.rename(columns=column_map, inplace=True)
    return stock_data


def calc_stock_metrics(stock_data: pd.DataFrame, config=None):
    c = {
        'period_rsi': 14,
        'period_macd_fast': 12,
        'period_macd_slow': 26,
        'period_macd_signal': 9,
        'period_bb': 20,
        'bb_std_dev': 2,
        'period_kdj': 9,
        'period_atr': 14,
        'period_roc': 10
    }
    if config is not None:
        for key in config:
            if key in c:
                c[key] = config[key]
    stock_data['ma5'] = stock_data['close'].rolling(window=5).mean()
    stock_data['ma10'] = stock_data['close'].rolling(window=10).mean()
    stock_data['ma20'] = stock_data['close'].rolling(window=20).mean()
    stock_data['rsi'] = calc_stock_rsi(stock_data, period=c['period_rsi'])
    stock_data['macd'], stock_data['macd_signal'], stock_data['macd_hist'] = calc_stock_macd(stock_data, c['period_macd_fast'], c['period_macd_slow'], c['period_macd_signal'])
    stock_data['bb_upper'], stock_data['bb_middle'], stock_data['bb_lower'] = calc_stock_bollinger_bands(stock_data, c['period_bb'], c['bb_std_dev'])
    stock_data['kdj_k'], stock_data['kdj_d'], stock_data['kdj_j'] = calc_stock_kdj(stock_data, c['period_kdj'])
    stock_data['volume_ma20'] = stock_data['volume'].rolling(window=20).mean()
    stock_data['volume_ratio20'] = stock_data['volume'] / stock_data['volume_ma20']
    stock_data['atr'] = calc_stock_atr(stock_data, c['period_atr'])
    stock_data['volatility'] = stock_data['atr'] / stock_data['close'] * 100
    stock_data['roc'] = stock_data['close'].pct_change(periods=c['period_roc']) * 100
    return stock_data


def calc_stock_rsi(stock_data: pd.DataFrame, period=14):
    delta = stock_data['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi


def calc_stock_macd(stock_data: pd.DataFrame, fast_period=12, slow_period=26, signal_period=9):
    ema_fast = stock_data['close'].ewm(span=fast_period, adjust=False).mean()
    ema_slow = stock_data['close'].ewm(span=slow_period, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist


def calc_stock_bollinger_bands(stock_data: pd.DataFrame, period=20, std_dev=2):
    middle = stock_data['close'].rolling(window=period).mean()
    std = stock_data['close'].rolling(window=period).std()
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    return upper, middle, lower


def calc_stock_kdj(stock_data: pd.DataFrame, period=9):
    lowest_low = stock_data['low'].rolling(window=period).min()
    highest_high = stock_data['high'].rolling(window=period).max()
    rsv = (stock_data['close'] - lowest_low) / (highest_high - lowest_low) * 100
    k_values = []
    k_prev = 50
    for rsv_value in rsv:
        if pd.isna(rsv_value):
            k_values.append(np.nan)
        else:
            k_curr = (2/3) * k_prev + (1/3) * rsv_value
            k_values.append(k_curr)
            k_prev = k_curr
    k = pd.Series(k_values)
    d_values = []
    d_prev = 50
    for k_value in k:
        if pd.isna(k_value):
            d_values.append(np.nan)
        else:
            d_curr = (2/3) * d_prev + (1/3) * k_value
            d_values.append(d_curr)
            d_prev = d_curr
    d = pd.Series(d_values)
    j = 3 * k - 2 * d
    return k, d, j


def calc_stock_atr(stock_data: pd.DataFrame, period=14):
    high = stock_data['high']
    low = stock_data['low']
    close = stock_data['close'].shift(1)
    tr1 = high - low
    tr2 = abs(high - close)
    tr3 = abs(low - close)
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr
