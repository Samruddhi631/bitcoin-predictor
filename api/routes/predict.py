# api/routes/predict.py
import numpy as np
import pandas as pd
import requests
import yfinance as yf
from flask import Blueprint, jsonify, current_app
from datetime import datetime

predict_bp = Blueprint('predict', __name__)

# ── Feature builder (same logic as Colab) ────────
def build_features(btc, sp500, fg):
    df = btc.copy()
    df['Date'] = pd.to_datetime(df['Date'])

    if sp500 is not None:
        sp500['Date'] = pd.to_datetime(sp500['Date'])
        df = df.merge(sp500, on='Date', how='left')
        df['SP500'] = df['SP500'].ffill().bfill()
    else:
        df['SP500'] = 4000.0

    if fg is not None:
        fg['Date'] = pd.to_datetime(fg['Date'])
        df = df.merge(fg, on='Date', how='left')
        df['FearGreed'] = df['FearGreed'].ffill().bfill()
    else:
        df['FearGreed'] = 50.0

    df['GoogleTrends'] = 50.0

    # Technical
    df['MA7']          = df['BTC_Close'].rolling(7).mean()
    df['MA30']         = df['BTC_Close'].rolling(30).mean()
    df['Price_Change'] = df['BTC_Close'].pct_change()
    df['Volatility']   = df['BTC_Close'].rolling(7).std()
    df['Lag1']         = df['BTC_Close'].shift(1)
    df['Lag2']         = df['BTC_Close'].shift(2)
    df['Lag3']         = df['BTC_Close'].shift(3)

    # RSI
    delta = df['BTC_Close'].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    df['RSI_14'] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df['BTC_Close'].ewm(span=12,
                                 adjust=False).mean()
    ema26 = df['BTC_Close'].ewm(span=26,
                                 adjust=False).mean()
    df['MACD']        = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(
                            span=9, adjust=False).mean()
    df['MACD_Hist']   = df['MACD'] - df['MACD_Signal']

    # Bollinger Bands
    rm  = df['BTC_Close'].rolling(20).mean()
    rs2 = df['BTC_Close'].rolling(20).std()
    df['BB_Upper']    = rm + (2 * rs2)
    df['BB_Lower']    = rm - (2 * rs2)
    df['BB_Width']    = ((df['BB_Upper'] -
                          df['BB_Lower']) / rm)
    df['BB_Position'] = ((df['BTC_Close'] -
                          df['BB_Lower']) /
                         (df['BB_Upper'] -
                          df['BB_Lower'] + 1e-9))

    # Volume
    df['Volume_MA7']   = df['Volume'].rolling(7).mean()
    df['Volume_Ratio'] = (df['Volume'] /
                          (df['Volume_MA7'] + 1e-9))

    # Sentiment
    df['FearGreed_Change'] = df['FearGreed'].diff()
    df['FearGreed_MA7']    = df['FearGreed'].rolling(
                                 7).mean()
    def sz(v):
        if v <= 25:   return 0
        elif v <= 45: return 1
        elif v <= 55: return 2
        elif v <= 75: return 3
        else:         return 4
    df['Sentiment_Zone'] = df['FearGreed'].apply(sz)
    df['Trends_Change']  = df['GoogleTrends'].diff()
    df['Trends_MA7']     = df['GoogleTrends'].rolling(
                               7).mean()

    # Halving
    halving_dates = [
        pd.Timestamp('2012-11-28'),
        pd.Timestamp('2016-07-09'),
        pd.Timestamp('2020-05-11'),
        pd.Timestamp('2024-04-20'),
        pd.Timestamp('2028-03-28'),
    ]
    d2n_l, dsl_l, cyc_l = [], [], []
    for date in df['Date']:
        future = [h for h in halving_dates if h > date]
        past   = [h for h in halving_dates if h <= date]
        nxt    = min(future) if future else halving_dates[-1]
        lst    = max(past)   if past   else halving_dates[0]
        d2n    = (nxt - date).days
        dsl    = (date - lst).days
        cyc    = (nxt - lst).days
        d2n_l.append(d2n)
        dsl_l.append(dsl)
        cyc_l.append(dsl / cyc if cyc > 0 else 0)

    df['Days_To_Halving']    = d2n_l
    df['Days_Since_Halving'] = dsl_l
    df['Halving_Cycle_Pct']  = cyc_l
    df['Post_Halving_180']   = (
        pd.Series(dsl_l) <= 180).astype(int).values

    # Calendar
    df['Day_of_Week'] = df['Date'].dt.dayofweek
    df['Month']       = df['Date'].dt.month
    df['Quarter']     = df['Date'].dt.quarter
    df['Is_Weekend']  = (df['Day_of_Week'] >= 5
                         ).astype(int)

    return df.dropna().reset_index(drop=True)

# ── Data fetchers ─────────────────────────────────
def fetch_btc():
    btc = yf.download('BTC-USD', period='60d',
                       interval='1d', progress=False,
                       auto_adjust=True)
    btc.columns = btc.columns.get_level_values(0)
    btc = btc[['Close','Volume']].copy()
    btc.columns = ['BTC_Close','Volume']
    btc.index = pd.to_datetime(btc.index).tz_localize(None)
    btc = btc.reset_index()
    btc.columns = ['Date','BTC_Close','Volume']
    return btc

def fetch_sp500():
    sp = yf.download('^GSPC', period='60d',
                      interval='1d', progress=False,
                      auto_adjust=True)
    sp.columns = sp.columns.get_level_values(0)
    sp = sp[['Close']].copy()
    sp.columns = ['SP500']
    sp.index = pd.to_datetime(sp.index).tz_localize(None)
    sp = sp.reset_index()
    sp.columns = ['Date','SP500']
    return sp

def fetch_fear_greed():
    url  = "https://api.alternative.me/fng/?limit=60"
    resp = requests.get(url, timeout=10)
    data = resp.json()['data']
    fg   = pd.DataFrame(data)
    fg['Date'] = pd.to_datetime(
        fg['timestamp'].astype(int), unit='s'
    ).dt.normalize()
    fg['FearGreed'] = fg['value'].astype(float)
    return fg[['Date','FearGreed']].sort_values('Date')

# ── /api/predict endpoint ─────────────────────────
@predict_bp.route('/api/predict')
def predict():
    try:
        models  = current_app.config['MODELS']
        config  = current_app.config['CONFIG']
        features = config['features']
        thresh   = config['optimal_threshold']

        # Fetch & build features
        btc  = fetch_btc()
        sp   = fetch_sp500()
        fg   = fetch_fear_greed()
        df   = build_features(btc, sp, fg)

        # Get last row
        last     = df[features].iloc[[-1]]
        scaled   = models['scaler_X'].transform(last)
        cur_price = float(df['BTC_Close'].iloc[-1])
        cur_date  = str(df['Date'].iloc[-1])[:10]

        # Return predictions
        ret_1d = float(models['scaler_y'].inverse_transform(
            models['xgb_return'].predict(
                scaled).reshape(-1,1))[0][0])
        ret_3d = float(models['scaler_y_3d'].inverse_transform(
            models['xgb_3day'].predict(
                scaled).reshape(-1,1))[0][0])
        ret_7d = float(models['scaler_y_7d'].inverse_transform(
            models['xgb_7day'].predict(
                scaled).reshape(-1,1))[0][0])

        # Ensemble direction
        xgb_p = models['ensemble_xgb'].predict_proba(
                    scaled)[0][1]
        rf_p  = models['ensemble_rf'].predict_proba(
                    scaled)[0][1]
        prob  = (0.6 * xgb_p) + (0.4 * rf_p)
        direction  = 'UP' if prob >= thresh else 'DOWN'
        confidence = prob if direction=='UP' else (1 - prob)
        conf_tier  = ('HIGH'   if confidence >= 0.62 else
                      'MEDIUM' if confidence >= 0.55 else
                      'LOW')

        # Market regime
        ret_20 = (df['BTC_Close'].iloc[-1] /
                  df['BTC_Close'].iloc[-20] - 1)
        regime = ('Bull'     if ret_20 > 0.05 else
                  'Bear'     if ret_20 < -0.05 else
                  'Sideways')

        # Fear & Greed latest
        fear_greed = int(fg['FearGreed'].iloc[-1])

        # Price history for chart (last 30 days)
        history = df[['Date','BTC_Close']].tail(30).copy()
        history['Date'] = history['Date'].dt.strftime(
                              '%Y-%m-%d')

        return jsonify({
            'success'       : True,
            'date'          : cur_date,
            'current_price' : round(cur_price, 2),
            'predictions'   : {
                'tomorrow' : {
                    'price'  : round(cur_price*(1+ret_1d),2),
                    'return' : round(ret_1d * 100, 3),
                },
                '3day' : {
                    'price'  : round(cur_price*(1+ret_3d),2),
                    'return' : round(ret_3d * 100, 3),
                },
                '7day' : {
                    'price'  : round(cur_price*(1+ret_7d),2),
                    'return' : round(ret_7d * 100, 3),
                },
            },
            'direction'     : {
                'signal'     : direction,
                'confidence' : round(confidence * 100, 1),
                'tier'       : conf_tier,
            },
            'market'        : {
                'regime'     : regime,
                'fear_greed' : fear_greed,
            },
            'price_history' : {
                'dates'  : history['Date'].tolist(),
                'prices' : history['BTC_Close'].tolist(),
            },
        })

    except Exception as e:
        return jsonify({
            'success' : False,
            'error'   : str(e)
        }), 500