import requests
import config
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, api_url):
        self.api_url = api_url
        self.session = requests.Session()

    def set_api_url(self, api_url):
        """Updates the API URL for the client."""
        if self.api_url != api_url:
            logger.info(f"LLMClient is now targeting new API URL: {api_url}")
            self.api_url = api_url

    def send_completion(self, prompt, session_id=None, turn=None):
        """Sends a prompt to the LLM API and returns the response."""
        payload = {
            "model": config.MODEL,
            "prompt": prompt,
            "temperature": config.TEMPERATURE,
            "seed": config.SEED,
            "stream": config.STREAM,
            "mode": config.CONTEXT_MODE,
            "user_id": config.USER_ID,
        }
        if session_id:
            payload["session_id"] = session_id
        if turn is not None:
            payload["turn"] = turn

        logger.debug(f"Sending payload to {self.api_url}: {payload}")

        try:
            response = self.session.post(self.api_url, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes
            json_response = response.json()
            logger.debug(f"Received response: {json_response}")
            return json_response, response.status_code
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with LLM API: {e}")
            print(f"Error communicating with LLM API: {e}")
            status_code = e.response.status_code if e.response is not None else None
            return None, status_code
