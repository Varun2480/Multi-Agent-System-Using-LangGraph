import logging # Import the logging module

class LoggerSettings:
    def logger_config(self):
        # --- Logging Configuration ---
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        LOGGER = logging.getLogger(__name__)
        return LOGGER

logger_settings = LoggerSettings()
LOGGER = logger_settings.logger_config()
