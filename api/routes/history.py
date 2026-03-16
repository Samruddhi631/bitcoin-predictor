# api/routes/history.py
import os
import pandas as pd
from flask import Blueprint, jsonify, request, current_app

history_bp = Blueprint('history', __name__)

@history_bp.route('/api/history')
def history():
    try:
        days     = int(request.args.get('days', 30))
        data_dir = current_app.config['DATA_DIR']
        log_path = os.path.join(data_dir,
                                'predictions_log.csv')

        if not os.path.exists(log_path):
            return jsonify({
                'success'     : True,
                'predictions' : [],
                'message'     : 'No predictions yet'
            })

        log = pd.read_csv(log_path)
        log = log.tail(days)
        log = log.fillna('pending')

        # Calculate stats
        completed = log[log['actual_price'] != 'pending']
        stats = {}
        if len(completed) > 0:
            stats = {
                'total_verified'  : len(completed),
                'direction_acc'   : round(float(
                    pd.to_numeric(
                        completed['direction_correct'],
                        errors='coerce').mean() * 100
                ), 1),
                'avg_error_usd'   : round(float(
                    pd.to_numeric(
                        completed['error_usd'],
                        errors='coerce').mean()
                ), 2),
                'avg_error_pct'   : round(float(
                    pd.to_numeric(
                        completed['error_pct'],
                        errors='coerce').mean()
                ), 2),
            }

        return jsonify({
            'success'     : True,
            'predictions' : log.to_dict('records'),
            'stats'       : stats,
            'total'       : len(log),
        })

    except Exception as e:
        return jsonify({
            'success' : False,
            'error'   : str(e)
        }), 500