import os
import asyncio
import pygame
import io
from lmnt.api import Speech

# Set your API key
os.environ["LMNT_API_KEY"] = "ak_2ByHtJzS3DqXqbp8ydXXTW"

def play_wake_sound(sound_file="wake.mp3"):
    """
    Play a wake sound effect from an MP3 file
    
    Args:
        sound_file (str): Path to the MP3 file to play (default: 'wake.mp3')
    """
    try:
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Load and play the sound file
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
            
    except pygame.error as e:
        print(f"Error playing wake sound: {e}")
    except FileNotFoundError:
        print(f"Wake sound file not found: {sound_file}")


def speak(text, voice='leah'):
    """
    Convert text to speech and play it immediately
    
    Args:
        text (str): Text to convert to speech
        voice (str): Voice to use (default: 'leah')
    """
    asyncio.run(_speak_async(text, voice))

async def _speak_async(text, voice):
    """Internal async function for speech synthesis"""
    async with Speech() as speech:
        synthesis = await speech.synthesize(text, voice)
    
    # Initialize pygame mixer if not already initialized
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    
    # Play audio directly from memory
    audio_data = io.BytesIO(synthesis['audio'])
    pygame.mixer.music.load(audio_data)
    pygame.mixer.music.play()
    
    # Wait for playback to finish
    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)

def speak_and_save(text, filename, voice='leah'):
    """
    Convert text to speech, save to file, and play it
    
    Args:
        text (str): Text to convert to speech
        filename (str): Path to save the audio file
        voice (str): Voice to use (default: 'leah')
    """
    asyncio.run(_speak_and_save_async(text, filename, voice))

async def _speak_and_save_async(text, filename, voice):
    """Internal async function for speech synthesis with file saving"""
    async with Speech() as speech:
        synthesis = await speech.synthesize(text, voice)
    
    # Save to file
    with open(filename, 'wb') as f:
        f.write(synthesis['audio'])
    
    # Initialize pygame mixer if not already initialized
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    
    # Play audio directly from memory
    audio_data = io.BytesIO(synthesis['audio'])
    pygame.mixer.music.load(audio_data)
    pygame.mixer.music.play()
    
    # Wait for playback to finish
    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)
