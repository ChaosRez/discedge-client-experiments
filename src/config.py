import os
import logging

# API Configuration
API_URL = "http://localhost:8081/completion"

# LLM Parameters
MODEL = "Qwen1.5-0.5B-Chat-Q4_K_M"
TEMPERATURE = 0
SEED = 123
STREAM = False
INFERENCE_MODE = "tokenized"

# Application Settings
USER_ID = "u1"
MODE = "interactive"  # "interactive" or "scenario"
SCENARIO_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_data', 'example_ruby.yml')

# Database Configuration
DB_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_PATH = os.path.join(DB_DIRECTORY, "chat.db")

# Logging Configuration
LOG_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'logs')
LOG_FILE = os.path.join(LOG_DIRECTORY, "client.log")
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
