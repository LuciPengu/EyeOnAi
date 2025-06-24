import sounddevice as sd
import wavio
import replicate
import os
import tempfile
from collections import deque
import numpy as np
asdfasfd
class VoiceRecognition:
    def __init__(self, samplerate=16000, channels=1):
        self.samplerate = samplerate
        self.channels = channels
        self.audio_buffer = deque(maxlen=samplerate*10)  # 10-sec buffer
        self.stream = None
        self.is_active = False
        
        # Set up Replicate API token if not already set
        if not os.environ.get("REPLICATE_API_TOKEN"):
            print("Warning: REPLICATE_API_TOKEN not set. Please set it with:")
        os.environ["REPLICATE_API_TOKEN"] = "r8_UqTVSqvFhzR8pAyBHFVSsLShg0c3Pjr0A5n2q"

    def start_voice(self):
        """Start non-blocking recording"""
        if self.stream and self.is_active:
            return "Already recording!"
        
        try:
            # Clear the buffer for new recording
            self.audio_buffer.clear()
            self.is_active = True
            
            self.stream = sd.InputStream(
                samplerate=self.samplerate,
                channels=self.channels,
                callback=self._audio_callback,
                dtype=np.float32  # Specify data type
            )
            self.stream.start()
            return "Recording started"
            
        except Exception as e:
            self.is_active = False
            return f"Error starting recording: {str(e)}"

    def _audio_callback(self, indata, frames, time, status):
        """Callback function for audio stream"""
        if status:
            print(f"Audio callback status: {status}")
        
        # Flatten the audio data and extend buffer
        if self.is_active:
            audio_data = indata.flatten() if self.channels == 1 else indata
            self.audio_buffer.extend(audio_data)

    def stop_voice(self):
        """Stop recording and transcribe audio"""
        try:
            if not self.is_active: 
                return "Not currently recording"
            
            self.is_active = False
            
            # Stop and close the audio stream
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            # Check if we have audio data
            if len(self.audio_buffer) == 0:
                return "No audio recorded"
            
            # Convert buffer to numpy array
            audio_data = np.array(list(self.audio_buffer), dtype=np.float32)
            print(f"Audio data shape: {audio_data.shape}")
            print(f"Audio data length: {len(audio_data)/self.samplerate:.2f} seconds")
            
            # Ensure audio data is in the right format for wavio
            if len(audio_data.shape) == 1:
                audio_data = audio_data.reshape(-1, 1)
            
            # Create temporary file and save audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
                
            try:
                # Write audio to temporary file
                # Convert float32 to int16 for better compatibility
                audio_int16 = (audio_data * 32767).astype(np.int16)
                wavio.write(tmp_path, audio_int16, self.samplerate, sampwidth=2)
                
                # Transcribe using Replicate
                with open(tmp_path, "rb") as f:
                    output = replicate.run(
                        "vaibhavs10/incredibly-fast-whisper:3ab86df6c8f54c11309d4d1f930ac292bad43ace52d10c80d87eb258b3c9f79c",
                        input={
                            "task": "transcribe",
                            "audio": f, 
                            "language": "None",
                            "timestamp": "chunk",
                            "batch_size": 64,
                            "diarise_audio": False
                        }
                    )
                
                # Clean up temporary file
                os.unlink(tmp_path)
                
                # Return transcription
                if isinstance(output, dict):
                    return output.get("text", output.get("transcription", "No transcription returned"))
                elif isinstance(output, str):
                    return output
                else:
                    return str(output)
                    
            except Exception as e:
                # Clean up temp file in case of error
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                return f"Error during transcription: {str(e)}"
                
        except Exception as e:
            return f"Error stopping recording: {str(e)}"
    
    def get_status(self):
        """Get current recording status"""
        return {
            "is_active": self.is_active,
            "buffer_length": len(self.audio_buffer),
            "buffer_duration_seconds": len(self.audio_buffer) / self.samplerate if self.audio_buffer else 0,
            "samplerate": self.samplerate,
            "channels": self.channels
        }
    
    def cleanup(self):
        """Clean up resources"""
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass
            self.stream = None
        self.is_active = False
        self.audio_buffer.clear()

# Example usage:
if __name__ == "__main__":
    # Make sure to set your Replicate API token
    # os.environ["REPLICATE_API_TOKEN"] = "your_token_here"
    
    voice_rec = VoiceRecognition()
    
    print("Voice Recognition Test")
    print("Commands: 'start' to begin recording, 'stop' to end and transcribe, 'status' for info, 'quit' to exit")
    
    try:
        while True:
            command = input("\nEnter command: ").strip().lower()
            
            if command == "start":
                result = voice_rec.start_voice()
                print(result)
                
            elif command == "stop":
                print("Processing audio...")
                result = voice_rec.stop_voice()
                print(f"Transcription: {result}")
                
            elif command == "status":
                status = voice_rec.get_status()
                print(f"Status: {status}")
                
            elif command == "quit":
                break
                
            else:
                print("Unknown command. Use 'start', 'stop', 'status', or 'quit'")
                
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        voice_rec.cleanup()
        print("Cleanup completed")
