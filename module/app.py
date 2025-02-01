from flask import Flask, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os
from pathlib import Path
from risk_calculator import calculate_download_risk
from config_wizard import run_config_wizard
from models import DownloadConfig

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")
csrf = CSRFProtect(app)

# Mock database
current_config = DownloadConfig(save_path="./downloads", max_size_mb=500)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/wizard')
def config_wizard():
    return render_template('wizard.html')

@app.route('/configure', methods=['POST'])
def handle_config():
    global current_config
    try:
        current_config = DownloadConfig(
            save_path=request.form['save_path'],
            max_size_mb=int(request.form['max_size'])
        )
        Path(current_config.save_path).mkdir(exist_ok=True)
        return jsonify({"status": "success", "config": current_config.dict()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/risk_stats')
def risk_stats():
    # Mock data - replace with real implementation
    return jsonify({
        "high_risk": 15,
        "medium_risk": 35,
        "low_risk": 50,
        "total_downloads": 100,
        "avg_size_mb": 42.5,
        "last_download": "2023-08-20 14:30:00"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
