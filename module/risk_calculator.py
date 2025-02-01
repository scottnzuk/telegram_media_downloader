import logging

logger = logging.getLogger(__name__)

def calculate_download_risk(media_size: int, media_type: str) -> float:
    """
    Calculate a risk score for media downloads based on size and type.
    
    Args:
        media_size: File size in bytes
        media_type: Media type string (e.g., 'video', 'photo')
    
    Returns:
        Risk score between 0.1 and 2.0
    """
    BASE_RISK = 0.1
    SIZE_RISK = min(media_size / (1024 ** 3), 1.0)  # Normalize to 0-1 for 1GB
    TYPE_RISK = 2.0 if media_type in ["video", "document"] else 1.5

    risk_score = BASE_RISK + (SIZE_RISK * TYPE_RISK)
    risk_score = min(risk_score, 2.0)  # Cap maximum risk

    if risk_score > 1.8:
        logger.warning(f"High-risk download detected: {risk_score:.2f} (Type: {media_type}, Size: {media_size} bytes)")
    elif risk_score > 1.2:
        logger.info(f"Medium-risk download: {risk_score:.2f}")
    
    return risk_score
