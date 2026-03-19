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

        # ✅ Return empty if file doesn't exist
        if not os.path.exists(log_path):
            print(f"⚠️ No predictions log at {log_path}")
            return jsonify({
                'success'     : True,
                'predictions' : [],
                'stats'       : {},
                'total'       : 0,
                'message'     : 'No predictions yet'
            })

        log = pd.read_csv(log_path)

        if len(log) == 0:
            return jsonify({
                'success'     : True,
                'predictions' : [],
                'stats'       : {},
                'total'       : 0,
            })

        log = log.tail(days)
        log = log.fillna('pending')

        # Calculate stats from completed predictions
        completed = log[log['actual_price'] != 'pending']
        stats = {}
        if len(completed) > 0:
            dir_correct = pd.to_numeric(
                completed['direction_correct'],
                errors='coerce').dropna()
            error_usd = pd.to_numeric(
                completed['error_usd'],
                errors='coerce').dropna()
            error_pct = pd.to_numeric(
                completed['error_pct'],
                errors='coerce').dropna()

            stats = {
                'total_verified' : len(completed),
                'direction_acc'  : round(float(
                    dir_correct.mean() * 100), 1)
                    if len(dir_correct) > 0 else 0,
                'avg_error_usd'  : round(float(
                    error_usd.mean()), 2)
                    if len(error_usd) > 0 else 0,
                'avg_error_pct'  : round(float(
                    error_pct.mean()), 2)
                    if len(error_pct) > 0 else 0,
            }

        return jsonify({
            'success'     : True,
            'predictions' : log.to_dict('records'),
            'stats'       : stats,
            'total'       : len(log),
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'success' : False,
            'error'   : str(e)
        }), 500