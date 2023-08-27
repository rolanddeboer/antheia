# Third-party libraries
import azure.cognitiveservices.speech as speechsdk
import logging
from tenacity import retry, stop_after_attempt, wait_fixed

# Antheia libraries
from config_manager import ConfigManager

logger = logging.getLogger(__name__)

class AzureManager:

    def __init__(self) -> None:
        self.config = ConfigManager.get_instance()
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.config.AZURE_SPEECH_KEY, 
            region=self.config.AZURE_SERVICE_REGION
        )
        self.speech_config.speech_synthesis_language = self.config.SPEECH_LANGUAGE

        format = speechsdk.SpeechSynthesisOutputFormat.Raw8Khz16BitMonoPcm if self.config.low_bandwidth else speechsdk.SpeechSynthesisOutputFormat.Raw16Khz16BitMonoPcm
        self.speech_config.set_speech_synthesis_output_format(format)
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)

    def _format_ssml(self, text) -> str:
        return f"<speak version='1.0' xmlns='https://www.w3.org/2001/10/synthesis' xml:lang='{self.config.SPEECH_LANGUAGE}'><voice  name='{self.config.SPEECH_VOICE}' rate='{self.config.SPEECH_RATE}' pitch='{self.config.SPEECH_PITCH}'>{text}</voice></speak>"

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry_error_cls=Exception)
    def _synthesize_text_to_speech_call(self, text) -> None:
        ssml_string = self._format_ssml(text)
        self.speech_synthesizer.speak_ssml_async(ssml_string).get()
    
    def synthesize_text_to_speech(self, text) -> None:
        try:
            self._synthesize_text_to_speech_call(text)
        except Exception as e:
            logger.error(f"Error synthesizing text to speech: {e}")
            # play pre-recorded apology message