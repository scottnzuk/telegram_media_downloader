from pathlib import Path
from typing import Optional
from config import DownloadConfig

def run_config_wizard(default_path: Optional[str] = None) -> DownloadConfig:
    """
    Interactive terminal configuration wizard with validation
    
    Args:
        default_path: Optional default save path
    
    Returns:
        Configured DownloadConfig object
    """
    print("\n" + "=" * 40)
    print("⚙️ Telegram Media Downloader Configuration Wizard")
    print("=" * 40 + "\n")

    # Path configuration
    default_path = default_path or "./downloads"
    while True:
        save_path = input(f"Enter default save path [{default_path}]: ").strip() or default_path
        if Path(save_path).is_dir():
            break
        try:
            Path(save_path).mkdir(parents=True, exist_ok=True)
            break
        except Exception as e:
            print(f"Error creating directory: {e}\nPlease try again.")

    # Size validation
    while True:
        size_input = input("Max file size in MB [500]: ").strip()
        max_size = 500 if not size_input else size_input
        
        try:
            max_size = int(max_size)
            if max_size > 0:
                break
            print("Error: Size must be greater than 0")
        except ValueError:
            print("Invalid number format. Please enter an integer.")

    print("\n✅ Configuration saved successfully!\n")
    return DownloadConfig(
        save_path=save_path,
        max_size_mb=max_size
    )
