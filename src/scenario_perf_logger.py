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
        self.headers = ['Timestamp', 'Operation', 'DurationMs', 'InferenceMode', 'ScenarioName', 'SessionID', 'Details']
        self.writer.writerow(self.headers)

    def set_session_id(self, session_id: str):
        """Sets the session ID for subsequent log entries."""
        self.session_id = session_id

    def log(self, operation: str, duration_ms: float, details: str = ""):
        """Logs a single performance record."""
        timestamp = datetime.now().isoformat()
        row = [
            timestamp,
            operation,
            f"{duration_ms:.2f}",
            self.inference_mode,
            self.scenario_name,
            self.session_id,
            details
        ]
        self.writer.writerow(row)
        self.file.flush()  # Ensure data is written to disk immediately

    def close(self):
        """Closes the CSV file."""
        self.file.close()

