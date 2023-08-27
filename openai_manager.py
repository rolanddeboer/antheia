# Built-in libraries
import io
import os
import subprocess
import tempfile
import logging

# Third-party libraries
import openai
from tenacity import retry, stop_after_attempt, wait_fixed
import tiktoken

# Antheia libraries
from config_manager import ConfigManager
from message_manager import MessageManager

logger = logging.getLogger(__name__)

class OpenAIManager:

    def __init__(self, model = 'gpt-4'):
        self.config = ConfigManager.get_instance()
        self.message_manager = MessageManager.get_instance()
        self.set_model(model)
        openai.organization = self.config.OPENAI_ORG
        openai.api_key = self.config.OPENAI_API_KEY

    def set_model(self, model):
        self.model = model
        self.prompt_price = self.config.OPENAI_PRICES[model]['prompt']
        self.completion_price = self.config.OPENAI_PRICES[model]['completion']

    def compute_cost(self, prompt_tokens, completion_tokens = 0):
        return (self.prompt_price * prompt_tokens + self.completion_price * completion_tokens) / 1000

    def get_cost_as_string(self, prompt_tokens, completion_tokens = 0):
        cost = self.compute_cost(prompt_tokens, completion_tokens)
        if cost < 0.01:
            return "less than a cent"
        if cost < 1:
            return f"{str(round(cost*100))} cents"
        return f"€{str(round(cost, 2))}"

    def estimate_cost(self):
        cost = self.get_cost_as_string(self.num_tokens_from_messages())

        print(self.config.colorize('FAIL', 'Estimated cost for prompt: ') + self.config.colorize('HEADER', str(cost)))

    def num_tokens_from_messages(self):
        # taken from https://platform.openai.com/docs/guides/gpt/managing-tokens
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = 0
        for message in self.message_manager.messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens

    def optimize_audio_file(self, audio_file) -> bytes:
        profile = self.config.PROMPT_AUDIO_PROFILES["speed" if self.config.low_bandwidth else "quality"]
        command = [
            'ffmpeg',
            '-i', audio_file,
            '-vn',
            '-c:a', 'aac',
            '-b:a', profile['bitrate'],
            '-ac', '1',
            '-ar', profile['sample_rate'],
            '-y',
            'pipe:1'
        ]
        with open(os.devnull, 'w') as dev_null_output:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=dev_null_output)
            output, _ = process.communicate()

        return output
    
    def transcribe(self, audio_file) -> str:
        try:
            optimized_audio_data = self.optimize_audio_file(audio_file)
            audio_buffer = io.BytesIO(optimized_audio_data)

            transcript = self._transcribe_call(audio_buffer)
        except Exception as e:
            logger.error(f"Error transcribing audio file {audio_file}: {e}")
            transcript = "An audio message was supposed to be transcribed and then entered here as a prompt. But something went wrong. Please tell the user that something went wrong transcribing their message."

        return transcript["text"]


    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry_error_cls=Exception)
    def _transcribe_call(self, audio_buffer):
        return openai.Audio.transcribe("whisper-1", audio_buffer)
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry_error_cls=Exception)
    def _generate_response_call(self):
        return openai.ChatCompletion.create(
            model=self.model,
            messages=self.message_manager.messages
        )
    
    def generate_response(self):
        if self.config.show_costs: 
            self.estimate_cost()
        
        try:
            response = self._generate_response_call()
            text = response["choices"][0]["message"]["content"]
            cost = self.get_cost_as_string(response["usage"]["prompt_tokens"], response["usage"]["completion_tokens"])

            if self.config.show_costs: 
                print(self.config.colorize('FAIL', 'Actual cost for prompt and response: ') + self.config.colorize('HEADER', str(cost)))
                print()
        except Exception as e:
            logger.error(f"Error generating response from {self.model}: {e}")
            text = "I'm sorry, I am not able to make contact with the OpenAI server at the moment."
        
        return text