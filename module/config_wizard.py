# module/config_wizard.py
import os
import yaml
import logging
from flask import Flask, render_template, request, redirect, url_for, session

from module.risk_calculator import compute_risk_score, get_safe_rate_limit

logger = logging.getLogger("config_wizard")

# Create a Flask app for the wizard.
wizard_app = Flask(__name__, template_folder="templates")
wizard_app.secret_key = "changeme"  # In production, use a secure, random key.

CONFIG_PATH = os.path.join(os.getcwd(), "config.yaml")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_config(config_data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(config_data, f, default_flow_style=False)
    logger.info("Configuration saved to config.yaml")

@wizard_app.route("/", methods=["GET", "POST"])
def wizard():
    if request.method == "POST":
        # Collect form data.
        try:
            account_age = int(request.form.get("account_age", "0"))
        except ValueError:
            account_age = 0
        vpn_usage = request.form.get("vpn_usage", "no")
        paid_status = request.form.get("paid_status", "free")  # "free" or "premium"
        
        # Instead of an automatic IP check, we ask the user to check their IP on AbuseIPDB.
        # The user will then provide a rating via a slider (1-5).
        try:
            slider_value = int(request.form.get("ip_reputation_rating", "3"))
        except ValueError:
            slider_value = 3
        # Map slider rating (1-5) to an IP risk factor between 0 and 2.
        # 1 -> 0, 5 -> 2 (linear mapping)
        ip_risk = (slider_value - 1) * 0.5
        
        # Compute the overall risk score using the provided ip risk.
        risk_score = compute_risk_score(account_age, ip_risk, vpn_usage)
        # Determine the suggested safe rate limit based on the risk score and account type.
        safe_rate = get_safe_rate_limit(risk_score, account_type=paid_status, use_safety_buffer=True)
        
        # Save the wizard data in the session.
        session["wizard"] = {
            "account_age_months": account_age,
            "vpn_usage": vpn_usage,
            "paid_status": paid_status,
            "ip_reputation_slider": slider_value,
            "computed_ip_risk": ip_risk,
            "risk_score": risk_score,
            "suggested_rate_limit": safe_rate
        }
        
        # Optionally, update the main configuration file.
        config_data = load_config()
        config_data["wizard_settings"] = session["wizard"]
        config_data["max_download_task"] = safe_rate if safe_rate > 0 else 1
        save_config(config_data)
        
        return redirect(url_for("dashboard"))
    return render_template("wizard.html")

@wizard_app.route("/dashboard")
def dashboard():
    wizard_data = session.get("wizard", {})
    return render_template("dashboard.html", wizard=wizard_data)

def run_wizard():
    wizard_app.run(host="0.0.0.0", port=5001, debug=True)

if __name__ == "__main__":
    run_wizard()
