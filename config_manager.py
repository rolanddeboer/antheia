from dotenv import load_dotenv
import json
import logging
import os

logger = logging.getLogger(__name__)
load_dotenv()

class ConfigManager:

    _instance = None
    _is_initialized = False

    @staticmethod
    def get_instance():
        if ConfigManager._instance is None:
            ConfigManager._instance = ConfigManager()
        return ConfigManager._instance

    def __init__(self):
        if ConfigManager._is_initialized:
            return
        self.CONFIG_FILE = 'config.json'
        with open(self.CONFIG_FILE, 'r') as file:
            self.config = json.load(file)
        self.show_costs = False
        self.low_bandwidth = False
        self.load_values()
        self.configure_logging()
        ConfigManager._is_initialized = True

    def configure_logging(self):
        logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def load_values(self):
        self.STORAGE_FILE = self.config['storage file']
        self.CONSOLE_IMAGE = self.config['console image']
        self.AZURE_SERVICE_REGION = self.config['azure service region']
        self.SPEECH_VOICE = self.config['speech voice']
        self.SPEECH_LANGUAGE = self.config['speech language']
        self.SPEECH_RATE = self.config['speech rate']
        self.SPEECH_PITCH = self.config['speech pitch']
        self.SYSTEM_MESSAGE = self.config['system message']
        self.OPENAI_PRICES = self.config['openai prices']
        self.PROMPT_AUDIO_PROFILES = self.config['prompt audio profiles']

        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.OPENAI_ORG = os.getenv('OPENAI_ORG')
        self.AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')

    def dump_config(self):
        print(self.colorize('FAIL', f"CONFIGURATION (loaded from {self.CONFIG_FILE}):"))
        with open(self.CONFIG_FILE, 'r') as file:
            print(json.dumps(json.load(file), indent=2))
        
        print(self.colorize('FAIL', f"\nMESSAGES (loaded from {self.STORAGE_FILE}):"))
        with open(self.STORAGE_FILE, 'r') as file:
            print(json.dumps(json.load(file), indent=2))
        print()

    def colorize(self, color, text):
        colors = {
            'HEADER': '\033[95m',
            'OKBLUE': '\033[94m',
            'OKGREEN': '\033[92m',
            'WARNING': '\033[93m',
            'FAIL': '\033[91m',
            'ENDC': '\033[0m',
            'BOLD': '\033[1m',
            'UNDERLINE': '\033[4m'
        }
        return colors[color] + text + colors['ENDC']

