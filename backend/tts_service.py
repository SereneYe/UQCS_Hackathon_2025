import os
import json
import tempfile
from typing import Optional
from google.cloud import texttospeech
from google.oauth2 import service_account
from sqlalchemy.orm import Session
import crud
import schemas
from models import AudioStatus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TTSService:
    """
    Google Cloud Text-to-Speech Service
    
    IMPORTANT: This service requires Google Cloud credentials to function.
    Before using TTS features, you must:
    1. Create a Google Cloud project and enable Text-to-Speech API
    2. Create a service account and download the JSON key file
    3. Place the key file in backend/credentials/ directory
    4. Set GOOGLE_APPLICATION_CREDENTIALS in your .env file
    
    Without proper credentials, all TTS endpoints will return 500 errors.
    """
    def __init__(self):
        self.client = self._create_tts_client()
    
    def _create_tts_client(self):
        """
        Create TTS client using environment variables for authentication
        
        Required setup:
        - GOOGLE_APPLICATION_CREDENTIALS: path to service account JSON key
        - OR GOOGLE_SERVICE_ACCOUNT_KEY: JSON key content as string
        """
        # Option 1: Use GOOGLE_APPLICATION_CREDENTIALS file path
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path and os.path.exists(credentials_path):
            return texttospeech.TextToSpeechClient()
        
        # Option 2: Use service account key content from env var
        service_account_key = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY")
        if service_account_key:
            try:
                service_account_info = json.loads(service_account_key)
                credentials = service_account.Credentials.from_service_account_info(
                    service_account_info
                )
                return texttospeech.TextToSpeechClient(credentials=credentials)
            except json.JSONDecodeError:
                raise ValueError("Invalid GOOGLE_SERVICE_ACCOUNT_KEY format")
        
        # Option 3: Try default credentials (for Google Cloud environments)
        try:
            return texttospeech.TextToSpeechClient()
        except Exception as e:
            raise ValueError(
                "Google Cloud credentials not found. Please set either:\n"
                "1. GOOGLE_APPLICATION_CREDENTIALS environment variable with path to service account key file\n"
                "2. GOOGLE_SERVICE_ACCOUNT_KEY environment variable with service account JSON content\n"
                f"Error: {str(e)}"
            )
    
    def synthesize_speech(
        self,
        text: str,
        voice_name: str = "en-US-Wavenet-D",
        language_code: str = "en-US",
        audio_format: str = "MP3"
    ) -> bytes:
        """
        Synthesize speech using Google Cloud Text-to-Speech API
        """
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )
        
        # Select the type of audio file
        audio_format_map = {
            "MP3": texttospeech.AudioEncoding.MP3,
            "WAV": texttospeech.AudioEncoding.LINEAR16,
            "OGG": texttospeech.AudioEncoding.OGG_OPUS
        }
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=audio_format_map.get(audio_format, texttospeech.AudioEncoding.MP3)
        )
        
        # Perform the text-to-speech request
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        return response.audio_content
    
    def get_available_voices(self, language_code: Optional[str] = None):
        """
        Get list of available voices from Google Cloud TTS
        """
        voices = self.client.list_voices(language_code=language_code)
        
        voice_list = []
        for voice in voices.voices:
            voice_info = {
                "name": voice.name,
                "language_codes": list(voice.language_codes),
                "ssml_gender": voice.ssml_gender.name
            }
            voice_list.append(voice_info)
        
        return voice_list
    
    def save_audio_file(self, audio_content: bytes, file_path: str) -> int:
        """
        Save audio content to file and return file size
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as audio_file:
            audio_file.write(audio_content)
        
        return len(audio_content)
    
    async def process_tts_request(
        self,
        db: Session,
        audio_create: schemas.AudioCreate
    ) -> schemas.Audio:
        """
        Process a complete TTS request: create DB record, synthesize speech, save file
        """
        # Create initial audio record
        audio_record = crud.create_audio(db=db, audio=audio_create)
        
        try:
            # Update status to processing
            crud.update_audio(db, audio_record.id, schemas.AudioUpdate(status=AudioStatus.PROCESSING))
            
            # Synthesize speech
            audio_content = self.synthesize_speech(
                text=audio_create.text_input,
                voice_name=audio_create.voice_name,
                language_code=audio_create.language_code,
                audio_format=audio_create.audio_format
            )
            
            # Generate file path
            file_extension = audio_create.audio_format.lower()
            file_path = f"audio_files/{audio_record.id}.{file_extension}"
            
            # Save audio file
            file_size = self.save_audio_file(audio_content, file_path)
            
            # Update record with file info and completed status
            update_data = schemas.AudioUpdate(
                status=AudioStatus.COMPLETED,
                file_path=file_path,
                file_size=file_size
            )
            
            return crud.update_audio(db, audio_record.id, update_data)
            
        except Exception as e:
            # Update status to failed on error
            crud.update_audio(db, audio_record.id, schemas.AudioUpdate(status=AudioStatus.FAILED))
            raise e

# Create a global TTS service instance
tts_service = TTSService()