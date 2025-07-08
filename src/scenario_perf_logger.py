import csv
import os
from datetime import datetime
import config

class PerformanceLogger:
    """Logs performance metrics of a scenario to a CSV file."""

    def __init__(self, inference_mode: str, scenario_name: str):
        self.inference_mode = inference_mode
        self.scenario_name = scenario_name
        self.session_id = None  # Will be set once the session starts

        os.makedirs(config.PERF_LOG_DIRECTORY, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_scenario_name = "".join(c for c in scenario_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
        filename = f"{timestamp}_{inference_mode}_{safe_scenario_name}.csv"
        self.filepath = os.path.join(config.PERF_LOG_DIRECTORY, filename)

        self.file = open(self.filepath, 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.headers = [
            'Timestamp', 'Operation', 'DurationMs', 'InferenceMode', 'ScenarioName', 'SessionID',
            'Turn', 'PromptLength', 'ContextLength', 'PromptTokens', 'PromptProcMs', 'PromptPerSecond', 'PredictedTokens', 'PredictedMs',
            'PredictedPerSecond', 'TokensCached', 'TokensEvaluated', 'ContextProcessed', 'RequestSize', 'HTTPStatusCode', 'ApiUrl', 'LocName', 'Retries', 'Details'
        ]
        self.writer.writerow(self.headers)

    def set_session_id(self, session_id: str):
        """Sets the session ID for subsequent log entries."""
        self.session_id = session_id

    def log(self, operation: str, duration_ms: float, details: dict = None):
        """Logs a single performance record."""
        timestamp = datetime.now().isoformat()
        if details is None:
            details = {}

        details_str = details.get('error', '')

        row = [
            timestamp,
            operation,
            f"{duration_ms:.2f}",
            self.inference_mode,
            self.scenario_name,
            self.session_id,
            details.get('turn', ''),
            details.get('prompt_length', ''),
            details.get('context_length', ''),
            details.get('prompt_tokens', ''),
            details.get('prompt_proc_ms', ''),
            details.get('prompt_per_second', ''),
            details.get('predicted_tokens', ''),
            details.get('predicted_ms', ''),
            details.get('predicted_per_second', ''),
            details.get('tokens_cached', ''),
            details.get('tokens_evaluated', ''),
            details.get('context_processed', ''),
            details.get('request_size', ''),
            details.get('http_status_code', ''),
            details.get('api_url', ''),
            details.get('location_name', ''),
            details.get('retries', ''),
            details_str
        ]
        self.writer.writerow(row)
        self.file.flush()  # Ensure data is written to disk immediately

    def close(self):
        """Closes the CSV file."""
        self.file.close()
