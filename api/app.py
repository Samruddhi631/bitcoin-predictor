# api/app.py
import os
import pickle
import json
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Add to top of api/app.py
import time

# Simple in-memory cache
_cache = {
    'prediction': None,
    'timestamp':  0,
}
CACHE_TTL = 3600  # 1 hour in seconds

def get_cached_prediction():
    now = time.time()
    if (_cache['prediction'] is not None and
            now - _cache['timestamp'] < CACHE_TTL):
        print("✅ Returning cached prediction")
        return _cache['prediction']
    return None

def set_cached_prediction(data):
    _cache['prediction'] = data
    _cache['timestamp']  = time.time()
    print("✅ Prediction cached")
load_dotenv()

app = Flask(__name__)

# ── CORS: allow React frontend to call this API ──
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5173",
            "https://bitcoin-predictor.vercel.app",  # ← add your Vercel URL
            os.getenv("FRONTEND_URL", "*")
        ]
    }
})

# ── Load all models once at startup ──────────────
MODELS_DIR = os.path.join(os.path.dirname(__file__),
                           'models')

def load_pickle(name):
    path = os.path.join(MODELS_DIR, f'{name}.pkl')
    if not os.path.exists(path):
        print(f"⚠️  {name}.pkl not found")
        return None
    with open(path, 'rb') as f:
        return pickle.load(f)

def load_json(name):
    path = os.path.join(MODELS_DIR, f'{name}.json')
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

print("Loading models...")
models = {
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
config = load_json('model_config')
print("✅ All models loaded")

# ── Register routes ───────────────────────────────
from routes.predict  import predict_bp
from routes.history  import history_bp
from routes.metrics  import metrics_bp

app.register_blueprint(predict_bp)
app.register_blueprint(history_bp)
app.register_blueprint(metrics_bp)

# Pass models to all blueprints via app config
app.config['MODELS'] = models
app.config['CONFIG'] = config
app.config['DATA_DIR'] = os.path.join(
    os.path.dirname(__file__), 'data')
os.makedirs(app.config['DATA_DIR'], exist_ok=True)

# ── Health check endpoint ─────────────────────────
@app.route('/api/health')
def health():
    loaded = {k: v is not None
              for k, v in models.items()}
    return {
        'status' : 'ok',
        'models' : loaded,
        'config' : config is not None
    }
@app.route('/api/warmup')
def warmup():
    return jsonify({'status': 'warm', 'ready': True})
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port)