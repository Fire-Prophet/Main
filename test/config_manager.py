# config_manager.py
import json
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConfigManager:
    def __init__(self, config_file="config.json"):
        """
        설정 파일 관리 클래스 초기화.
        """
        self.config_file = config_file
        self.config = {}
        self._load_config()
        logging.info(f"ConfigManager initialized for {config_file}.")

    def _load_config(self):
        """
        파일에서 설정을 로드합니다. 파일이 없으면 기본값을 사용합니다.
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            logging.info(f"Configuration loaded from {self.config_file}.")
        else:
            self.config = {
                "database_url": "sqlite:///./test.db",
                "api_key": "your_default_api_key",
                "log_level": "INFO",
                "max_retries": 3
            }
            self._save_config() # 초기 설정 저장
            logging.warning(f"Config file {self.config_file} not found. Default config loaded and saved.")

    def _save_config(self):
        """
        현재 설정을 파일에 저장합니다.
        """
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
        logging.info(f"Configuration saved to {self.config_file}.")

    def get_setting(self, key, default=None):
        """
        특정 설정 값을 가져옵니다.
        """
        value = self.config.get(key, default)
        logging.debug(f"Getting setting '{key}': {value}")
        return value

    def set_setting(self, key, value):
        """
        특정 설정 값을 설정하고 저장합니다.
        """
        self.config[key] = value
        self._save_config()
        logging.info(f"Setting '{key}' updated to '{value}'.")

# 예시 사용
if __name__ == "__main__":
    # config.json 파일이 없으면 새로 생성됩니다.
    manager = ConfigManager("my_app_config.json")
    db_url = manager.get_setting("database_url")
    print(f"Database URL: {db_url}")

    manager.set_setting("log_level", "DEBUG")
    new_log_level = manager.get_setting("log_level")
    print(f"New Log Level: {new_log_level}")

    api_key = manager.get_setting("api_key", "default_key_if_not_found")
    print(f"API Key: {api_key}")

    # my_app_config.json 파일이 생성되거나 업데이트되어 있을 것입니다.
