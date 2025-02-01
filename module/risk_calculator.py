# module/risk_calculator.py
import logging
import time

logger = logging.getLogger("risk_calculator")

def compute_risk_score(account_age_months: int, ip_risk: float, vpn_usage: str) -> float:
    """
    Compute a risk score based on account age, IP reputation, and VPN usage.
    
    Parameters:
      account_age_months: Age of the Telegram account in months.
      ip_risk: A risk factor for the IP as determined by user input (from a slider),
               where 1 (super clean) maps to 0 and 5 (many reports) maps to 2.
      vpn_usage: String indicating VPN usage. Expected values: "no", "free", "paid", or "optional".
      
    Returns:
      A float risk score where a lower score means less risk.
      
    Risk Calculation:
      - Account Age:
         * Less than 6 months: risk factor = 2
         * 6 to 24 months: risk factor = 1.5
         * More than 24 months: risk factor = 1
      - VPN Usage:
         * "no": risk factor = 0
         * "paid": risk factor = 0.5
         * "free": risk factor = 2
         * "optional" (or others): risk factor = 1
      - IP Reputation:
         * Directly use the provided ip_risk (range: 0 to 2)
    """
    # Account age risk factor.
    if account_age_months < 6:
        account_risk = 2
    elif account_age_months < 24:
        account_risk = 1.5
    else:
        account_risk = 1

    # VPN usage risk factor.
    vpn_usage_lower = vpn_usage.lower()
    if vpn_usage_lower == "no":
        vpn_risk = 0
    elif vpn_usage_lower == "paid":
        vpn_risk = 0.5
    elif vpn_usage_lower == "free":
        vpn_risk = 2
    else:
        vpn_risk = 1

    # ip_risk is already a value between 0 and 2.
    total_risk = account_risk + vpn_risk + ip_risk
    logger.info(f"Risk factors - Account: {account_risk}, VPN: {vpn_risk}, IP: {ip_risk} => Total Risk: {total_risk}")
    return total_risk

def get_safe_rate_limit(risk_score: float, account_type: str = "free", use_safety_buffer: bool = True) -> int:
    """
    Calculate a safe API rate limit based on risk factors and account type.
    
    Parameters:
      risk_score: The computed risk score from compute_risk_score.
      account_type: "free" or "premium". Premium accounts receive a boost.
      use_safety_buffer: Whether to apply a 10% safety buffer.
      
    Returns:
      An integer representing the suggested rate limit (e.g., messages per minute).
      
    Calculation:
      - Base rate = 30 messages per minute (mpm).
      - Subtract a risk penalty: risk_score * 5.
      - Optionally apply a 10% buffer.
      - For premium accounts, multiply the result by a premium multiplier (e.g., 1.2x).
    """
    base_rate = 30
    adjusted = base_rate - (risk_score * 5)
    safe_rate = int(adjusted * 0.9) if use_safety_buffer else int(adjusted)

    if account_type.lower() == "premium":
        premium_multiplier = 1.2  # Premium users get a 20% boost.
        safe_rate = int(safe_rate * premium_multiplier)
        logger.info(f"Premium account: Boosting safe rate to {safe_rate} mpm.")
    else:
        logger.info(f"Free account safe rate: {safe_rate} mpm.")

    return safe_rate

def handle_flood_wait(current_rate: int) -> int:
    """
    Handle a FloodWait error by waiting and reducing the download rate.
    
    If a FloodWait error is encountered (e.g., due to exceeding Telegram API limits),
    this function waits for at least 40 seconds, reduces the current rate limit by 15%,
    and logs the change (so that the UI/user can be updated).
    
    Parameters:
      current_rate: The current safe rate limit in messages per minute.
      
    Returns:
      The new safe rate limit after reduction.
    """
    logger.warning("FloodWait error encountered. Waiting for 40 seconds before retrying...")
    time.sleep(40)
    new_rate = int(current_rate * 0.85)
    logger.info(f"Reducing rate limit by 15%. New safe rate: {new_rate} mpm.")
    return new_rate
