import requests
import config
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, api_url):
        self.api_url = api_url

    def send_completion(self, prompt, session_id=None):
        """Sends a prompt to the LLM API and returns the response."""
        payload = {
            "model": config.MODEL,
            "prompt": prompt,
            "temperature": config.TEMPERATURE,
            "seed": config.SEED,
            "stream": config.STREAM,
            "mode": config.MODE,
            "user_id": config.USER_ID,
        }
        if session_id:
            payload["session_id"] = session_id

        logger.debug(f"Sending payload to {self.api_url}: {payload}")

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes
            json_response = response.json()
            logger.debug(f"Received response: {json_response}")
            return json_response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with LLM API: {e}")
            print(f"Error communicating with LLM API: {e}")
            return None