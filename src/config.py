import os
import logging

# API Configuration
DEFAULT_API_URL = "http://localhost:8081/completion"

# LLM Parameters
MODEL = "Qwen1.5-0.5B-Chat-Q4_K_M"
TEMPERATURE = 0
SEED = 123
STREAM = False
CONTEXT_MODE = "tokenized" # "tokenized" or "raw" or "client-side"

# Application Settings
USER_ID = "u1"
MODE = "scenario"  # "interactive" or "scenario"
SCENARIO_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_data', 'example_robo_longer.yml')#'moving_robo_longer.yml')

# Database Configuration
DB_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_PATH = os.path.join(DB_DIRECTORY, "chat.db")

# Logging Configuration
LOG_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'logs')
PERF_LOG_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'logs', 'experiments')
LOG_FILE = os.path.join(LOG_DIRECTORY, "client.log")
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
