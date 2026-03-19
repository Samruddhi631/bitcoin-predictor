# api/app.py
import os
import pickle
import json
import time
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ── CORS ──────────────────────────────────────────
CORS(app, resources={
    r"/api/*": {
        "origins": "*"  # Allow all origins
    }
})

# ── Cache ─────────────────────────────────────────
_cache = {
    'prediction': None,
    'timestamp':  0,
}
CACHE_TTL = 3600

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

# ── Load models ───────────────────────────────────
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

# ── Register blueprints ───────────────────────────
from routes.predict import predict_bp
from routes.history import history_bp
from routes.metrics import metrics_bp

app.register_blueprint(predict_bp)
app.register_blueprint(history_bp)
app.register_blueprint(metrics_bp)

app.config['MODELS']   = models
app.config['CONFIG']   = config
app.config['DATA_DIR'] = os.path.join(
    os.path.dirname(__file__), 'data')
os.makedirs(app.config['DATA_DIR'], exist_ok=True)

# Make cache functions available to routes
app.get_cached_prediction = get_cached_prediction
app.set_cached_prediction = set_cached_prediction

# ── Endpoints ─────────────────────────────────────
@app.route('/')
def index():
    return jsonify({
        'name'    : 'Bitcoin Predictor API',
        'status'  : 'running',
        'version' : '1.0.0',
    })

@app.route('/api/health')
def health():
    loaded = {k: v is not None for k, v in models.items()}
    return jsonify({
        'status'  : 'ok',
        'models'  : loaded,
        'config'  : config is not None,
    })

@app.route('/api/warmup')
def warmup():
    # ✅ Simple endpoint — wakes server instantly
    return jsonify({
        'status' : 'warm',
        'ready'  : True,
        'models' : all(v is not None for v in models.values())
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
