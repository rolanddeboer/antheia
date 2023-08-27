from config_manager import ConfigManager
import json

class MessageManager:

    _instance = None
    _is_initialized = False

    @staticmethod
    def get_instance():
        if MessageManager._instance is None:
            MessageManager._instance = MessageManager()
        return MessageManager._instance

    def __init__(self):
        if MessageManager._is_initialized:
            return
        self.config = ConfigManager.get_instance()
        self.load_messages()
        MessageManager._is_initialized = True

    def load_messages(self):
        """Load messages from the storage file."""
        try:
            with open(self.config.STORAGE_FILE, 'r') as file:
                self.messages = json.load(file)
        except:
            self.clear_messages()
            pass

    def clear_messages(self):
        self.messages = []
        self.add_message(self.config.SYSTEM_MESSAGE, "system")

    def save_messages(self):
        """Save messages to the storage file."""
        with open(self.config.STORAGE_FILE, 'w') as file:
            json.dump(self.messages, file)

    def add_message(self, message, role):
        """Add a message with the specified role."""
        self.messages.append({"role": role, "content": message})
        self.save_messages()

    def add_user_message(self, message):
        """Add a user message."""
        self.add_message(message, "user")

    def add_assistant_message(self, message):
        """Add an assistant message."""
        self.add_message(message, "assistant")
