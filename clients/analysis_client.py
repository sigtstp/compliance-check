import os
import json
import requests
from requests.auth import HTTPBasicAuth
from exceptions.model_api_error import ModelAPIError


class AnalysisClient:
    """Client for communicating with the model API to analyze requirements and user stories."""

    def __init__(self):
        self.__model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.__url = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
        self.__user = os.getenv("OLLAMA_USER", None)
        self.__password = os.getenv("OLLAMA_PASSWORD", None)

    def get_response(self, prompt: str) -> str:
        """Send a prompt to the model API and return the response as a string."""
        print("Analyzing input requirements...")

        try:
            payload = self.__create_payload(prompt)
            auth = self.__configure_auth()

            response = requests.post(self.__url, json=payload, auth=auth)
            response.raise_for_status()

            response_json = response.json()
            
            if "response" not in response_json:
                raise ModelAPIError(
                    "Model API response does not contain 'response' field."
                )
            
            return response_json["response"]
        except requests.exceptions.RequestException as e:
            raise ModelAPIError(f"Model API request failed: {e}")
        except json.JSONDecodeError:
            raise ModelAPIError("Model API returned invalid JSON.")

    def __create_payload(self, prompt: str) -> dict:
        """Create the payload for the model API request."""
        payload = {
            "model": self.__model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }

        return payload

    def __configure_auth(self):
        """Configure HTTP Basic Authentication if credentials are provided."""
        if self.__user and self.__password:
            return HTTPBasicAuth(self.__user, self.__password)

        return None
