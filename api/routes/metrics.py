# api/routes/metrics.py
from flask import Blueprint, jsonify, current_app

metrics_bp = Blueprint('metrics', __name__)

@metrics_bp.route('/api/metrics')
def metrics():
    try:
        models  = current_app.config['MODELS']
        config  = current_app.config['CONFIG']

        # Feature importance from XGBoost
        feat_imp = {}
        if models['xgb_return'] and config:
            features = config.get('features', [])
            scores   = models['xgb_return'] \
                             .feature_importances_
            feat_imp = dict(zip(features,
                [round(float(s), 4) for s in scores]))
            feat_imp = dict(sorted(
                feat_imp.items(),
                key=lambda x: x[1],
                reverse=True
            ))

        return jsonify({
            'success' : True,
            'model_metrics' : {
                'direction_accuracy'    : 54.3,
                'high_conf_accuracy'    : 57.4,
                'walk_forward_accuracy' : 52.6,
                'stability_gap'        : 1.7,
                'training_rows'        : 3298,
                'features_count'       : len(
                    config.get('features', [])),
                'training_period'      : '2017-2026',
                'optimal_threshold'    : config.get(
                    'optimal_threshold', 0.53),
                'last_trained'         : config.get(
                    'last_trained', 'Unknown'),
            },
            'feature_importance' : feat_imp,
            'top_features'       : list(feat_imp.keys())[:10],
        })

    except Exception as e:
        return jsonify({
            'success' : False,
            'error'   : str(e)
        }), 500


@metrics_bp.route('/api/price-history')
def price_history():
    """Returns longer price history for charts"""
    try:
        import yfinance as yf
        import pandas as pd
        from flask import request

        days = int(request.args.get('days', 90))
        btc  = yf.download('BTC-USD',
                            period=f'{days}d',
                            interval='1d',
                            progress=False,
                            auto_adjust=True)
        btc.columns = btc.columns.get_level_values(0)
        btc.index   = pd.to_datetime(
                          btc.index).tz_localize(None)
        btc = btc.reset_index()
        btc.columns = ['Date'] + list(btc.columns[1:])

        return jsonify({
            'success' : True,
            'dates'   : btc['Date'].dt.strftime(
                            '%Y-%m-%d').tolist(),
            'prices'  : btc['Close'].round(2).tolist(),
            'volumes' : btc['Volume'].tolist(),
        })

    except Exception as e:
        return jsonify({
            'success' : False,
            'error'   : str(e)
        }), 500