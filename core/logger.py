import logging # Import the logging module

class LoggerSettings:
    def logger_config(self):
        # --- Logging Configuration ---
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        LOGGER = logging.getLogger(__name__)
        return LOGGER

LOGGER = LoggerSettings().logger_config()
