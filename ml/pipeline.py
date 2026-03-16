# ml/pipeline.py
# GitHub Actions runs this every day at 6am automatically

import os
import sys
import pickle
import json
import pandas as pd
import numpy as np
import requests
import yfinance as yf
from datetime import datetime, timedelta

# ── Paths ─────────────────────────────────────────
ROOT_DIR    = os.path.dirname(os.path.dirname(
                  os.path.abspath(__file__)))
MODELS_DIR  = os.path.join(ROOT_DIR, 'api', 'models')
DATA_DIR    = os.path.join(ROOT_DIR, 'api', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# ── Load models ───────────────────────────────────
def load_pickle(name):
    with open(os.path.join(MODELS_DIR,
                           f'{name}.pkl'), 'rb') as f:
        return pickle.load(f)

def load_config():
    with open(os.path.join(MODELS_DIR,
                           'model_config.json')) as f:
        return json.load(f)

# ── Fetch data ────────────────────────────────────
def fetch_btc(days=60):
    btc = yf.download('BTC-USD', period=f'{days}d',
                       interval='1d', progress=False,
                       auto_adjust=True)
    btc.columns = btc.columns.get_level_values(0)
    btc = btc[['Close','Volume']].copy()
    btc.columns = ['BTC_Close','Volume']
    btc.index = pd.to_datetime(btc.index).tz_localize(None)
    btc = btc.reset_index()
    btc.columns = ['Date','BTC_Close','Volume']
    return btc

def fetch_sp500(days=60):
    sp = yf.download('^GSPC', period=f'{days}d',
                      interval='1d', progress=False,
                      auto_adjust=True)
    sp.columns = sp.columns.get_level_values(0)
    sp = sp[['Close']].copy()
    sp.columns = ['SP500']
    sp.index = pd.to_datetime(sp.index).tz_localize(None)
    sp = sp.reset_index()
    sp.columns = ['Date','SP500']
    return sp

def fetch_fear_greed(days=60):
    url  = f"https://api.alternative.me/fng/?limit={days}"
    resp = requests.get(url, timeout=15)
    data = resp.json()['data']
    fg   = pd.DataFrame(data)
    fg['Date'] = pd.to_datetime(
        fg['timestamp'].astype(int), unit='s'
    ).dt.normalize()
    fg['FearGreed'] = fg['value'].astype(float)
    return fg[['Date','FearGreed']].sort_values('Date')

# ── Build features ────────────────────────────────
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
    df['MA7']          = df['BTC_Close'].rolling(7).mean()
    df['MA30']         = df['BTC_Close'].rolling(30).mean()
    df['Price_Change'] = df['BTC_Close'].pct_change()
    df['Volatility']   = df['BTC_Close'].rolling(7).std()
    df['Lag1']         = df['BTC_Close'].shift(1)
    df['Lag2']         = df['BTC_Close'].shift(2)
    df['Lag3']         = df['BTC_Close'].shift(3)

    delta = df['BTC_Close'].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    df['RSI_14'] = 100 - (100 / (1 + rs))

    ema12 = df['BTC_Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['BTC_Close'].ewm(span=26, adjust=False).mean()
    df['MACD']        = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9,
                            adjust=False).mean()
    df['MACD_Hist']   = df['MACD'] - df['MACD_Signal']

    rm  = df['BTC_Close'].rolling(20).mean()
    rs2 = df['BTC_Close'].rolling(20).std()
    df['BB_Upper']    = rm + (2 * rs2)
    df['BB_Lower']    = rm - (2 * rs2)
    df['BB_Width']    = (df['BB_Upper'] -
                         df['BB_Lower']) / rm
    df['BB_Position'] = ((df['BTC_Close'] -
                          df['BB_Lower']) /
                         (df['BB_Upper'] -
                          df['BB_Lower'] + 1e-9))
    df['Volume_MA7']   = df['Volume'].rolling(7).mean()
    df['Volume_Ratio'] = df['Volume'] / (
                             df['Volume_MA7'] + 1e-9)
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
        nxt = min(future) if future else halving_dates[-1]
        lst = max(past)   if past   else halving_dates[0]
        d2n = (nxt - date).days
        dsl = (date - lst).days
        cyc = (nxt - lst).days
        d2n_l.append(d2n)
        dsl_l.append(dsl)
        cyc_l.append(dsl / cyc if cyc > 0 else 0)

    df['Days_To_Halving']    = d2n_l
    df['Days_Since_Halving'] = dsl_l
    df['Halving_Cycle_Pct']  = cyc_l
    df['Post_Halving_180']   = (
        pd.Series(dsl_l) <= 180).astype(int).values
    df['Day_of_Week'] = df['Date'].dt.dayofweek
    df['Month']       = df['Date'].dt.month
    df['Quarter']     = df['Date'].dt.quarter
    df['Is_Weekend']  = (df['Day_of_Week'] >= 5
                         ).astype(int)

    return df.dropna().reset_index(drop=True)

# ── Main pipeline ─────────────────────────────────
def run():
    print(f"🚀 Pipeline started — "
          f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Load everything
    config  = load_config()
    features = config['features']
    thresh   = config['optimal_threshold']
    models  = {
        'xgb_return'   : load_pickle('xgb_return_model'),
        'xgb_3day'     : load_pickle('xgb_3day_return'),
        'xgb_7day'     : load_pickle('xgb_7day_return'),
        'ensemble_xgb' : load_pickle('ensemble_xgb_clf'),
        'ensemble_rf'  : load_pickle('ensemble_rf_clf'),
        'scaler_X'     : load_pickle('scaler_X'),
        'scaler_y'     : load_pickle('scaler_y'),
        'scaler_y_3d'  : load_pickle('scaler_y_3day'),
        'scaler_y_7d'  : load_pickle('scaler_y_7day'),
    }
    print("✅ Models loaded")

    # Fetch data
    btc = fetch_btc()
    sp  = fetch_sp500()
    fg  = fetch_fear_greed()
    df  = build_features(btc, sp, fg)
    print(f"✅ Data fetched — {len(df)} rows")

    # Predict
    last    = df[features].iloc[[-1]]
    scaled  = models['scaler_X'].transform(last)
    cur     = float(df['BTC_Close'].iloc[-1])

    ret_1d  = float(models['scaler_y'].inverse_transform(
        models['xgb_return'].predict(
            scaled).reshape(-1,1))[0][0])
    ret_3d  = float(models['scaler_y_3d'].inverse_transform(
        models['xgb_3day'].predict(
            scaled).reshape(-1,1))[0][0])
    ret_7d  = float(models['scaler_y_7d'].inverse_transform(
        models['xgb_7day'].predict(
            scaled).reshape(-1,1))[0][0])

    xgb_p   = models['ensemble_xgb'].predict_proba(
                  scaled)[0][1]
    rf_p    = models['ensemble_rf'].predict_proba(
                  scaled)[0][1]
    prob    = (0.6 * xgb_p) + (0.4 * rf_p)
    direction  = 'UP' if prob >= thresh else 'DOWN'
    confidence = prob if direction=='UP' else 1-prob

    today = datetime.now().strftime('%Y-%m-%d')

    # Save to predictions log
    log_path = os.path.join(DATA_DIR,
                             'predictions_log.csv')
    if os.path.exists(log_path):
        log = pd.read_csv(log_path)
    else:
        log = pd.DataFrame()

    # Fill yesterday's actual price
    if len(log) > 0:
        yesterday = (datetime.now() -
                     timedelta(days=1)
                     ).strftime('%Y-%m-%d')
        mask = log['date'] == yesterday
        if mask.any():
            yest = df[
                df['Date'].dt.strftime('%Y-%m-%d')
                == yesterday]
            if len(yest) > 0:
                actual = float(
                    yest['BTC_Close'].iloc[-1])
                log.loc[mask, 'actual_price'] = actual
                pred = float(log.loc[
                    mask,'pred_tomorrow'].values[0])
                log.loc[mask,'error_usd'] = abs(
                    actual - pred)
                log.loc[mask,'error_pct'] = (
                    abs(actual-pred)/actual*100)
                was_up  = actual > float(log.loc[
                    mask,'current_price'].values[0])
                pred_up = direction == 'UP'
                log.loc[mask,'direction_correct'] = int(
                    was_up == pred_up)
                print(f"✅ Yesterday verified: "
                      f"${actual:,.2f} actual")

    # Add today
    new_row = pd.DataFrame([{
        'date'           : today,
        'current_price'  : round(cur, 2),
        'pred_tomorrow'  : round(cur*(1+ret_1d), 2),
        'pred_3day'      : round(cur*(1+ret_3d), 2),
        'pred_7day'      : round(cur*(1+ret_7d), 2),
        'return_1d'      : round(ret_1d*100, 3),
        'return_3d'      : round(ret_3d*100, 3),
        'return_7d'      : round(ret_7d*100, 3),
        'direction'      : direction,
        'confidence'     : round(confidence*100, 1),
        'actual_price'   : None,
        'error_usd'      : None,
        'error_pct'      : None,
        'direction_correct': None,
    }])
    log = pd.concat([log, new_row],
                     ignore_index=True)
    log.to_csv(log_path, index=False)

    print(f"✅ Prediction saved: "
          f"${cur:,.2f} → "
          f"${cur*(1+ret_1d):,.2f} ({direction})")
    print("✅ Pipeline complete!")
    return True

if __name__ == '__main__':
    success = run()
    sys.exit(0 if success else 1)