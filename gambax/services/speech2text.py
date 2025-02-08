from openai import OpenAI
from typing import Optional, List, Dict, Any

from gambax.services import Service

class SpeechToTextService(Service):

    def __init__(self, name: str = "SpeechToTextService", description: str = "Converts speech to text using OpenAI's Whisper API"):
        super().__init__(name=name, input_signature=["audio_file"], output_signature=["transcription"], description=description)
        self.client = OpenAI()

    def request_impl(self, audio_file: str) -> Dict[str, Any]:
        response = self.client.Audio.transcribe(
            model="whisper-1",
            file=open(audio_file, "rb")
        )
        transcription = response.get("text", "")
        return {"transcription": transcription}

    def get_tool(self) -> str:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "audio_file": {
                        "type": "string",
                        "description": "Path to the audio file to be transcribed."
                    }
                },
                "required": ["audio_file"]
            }
        }
