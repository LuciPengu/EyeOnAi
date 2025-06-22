from flask import Flask, render_template, request, jsonify
import json
import replicate
import re
import os
from computer_commands import AccessibilityCommands
from voice_commands import VoiceRecognition
import keyboard
import threading
import requests
import sys
import time
from PyQt5 import QtWidgets, QtCore, QtGui
import signal
from lmnt import speak, speak_and_save
import google as genai


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

class AccessibilityChatbot:
    def __init__(self):
        """Initialize the chatbot with Replicate API token"""
        self.commands = AccessibilityCommands()
        self.voice_recognition = VoiceRecognition()
        

        # Set API token directly in the environment
        os.environ["REPLICATE_API_TOKEN"] = "r8_UqTVSqvFhzR8pAyBHFVSsLShg0c3Pjr0A5n2q"
        
        # Initialize replicate client
        replicate.api_token = os.environ["REPLICATE_API_TOKEN"]
        
        # System prompt for the LLM
        self.system_prompt = """You are an accessibility assistant that helps users control their computer through voice commands and text. 

You can execute the following types of commands:

WINDOW MANAGEMENT:
- open_application(app_name) - Open an application
- close_application(app_name) - Close an application  
- minimize_window() - Minimize active window
- maximize_window() - Maximize active window
- close_window() - Close active window
- switch_window() - Switch between windows
- get_active_windows() - List active applications

FILE OPERATIONS:
- create_file(filepath, content) - Create a new file
- create_folder(folderpath) - Create a new folder
- delete_file(filepath) - Delete a file
- delete_folder(folderpath) - Delete a folder
- copy_file(source, destination) - Copy a file
- move_file(source, destination) - Move a file
- rename_file(old_path, new_path) - Rename a file/folder
- search_files(directory, pattern) - Search for files
- list_directory(directory) - List directory contents

SYSTEM SETTINGS:
- set_brightness(level) - Set brightness 0-100 (Windows only)
- shutdown_system() - Shutdown computer
- restart_system() - Restart computer

BROWSER OPERATIONS:
- open_url(url) - Open a URL
- browser_back() - Go back
- browser_forward() - Go forward  
- refresh_page() - Refresh page
- new_tab() - Open new tab
- close_tab() - Close current tab
- switch_tab(direction) - Switch tabs ("next" or "previous")

ACCESSIBILITY FEATURES:
- click_at(x, y) - Click at coordinates
- type_text(text) - Type text
- press_key(key) - Press key (use + for combinations like "ctrl+c")
- scroll(direction, clicks) - Scroll ("up" or "down")
- read_screen(x, y) - Take screenshot or check pixel color

When a user asks you to do something, determine which function(s) to call and format your response as:
EXECUTE: function_name(parameters)

For example:
- "Open Chrome" → EXECUTE: open_application("chrome")
- "Create a file called test.txt" → EXECUTE: create_file("test.txt", "")
- "Press Ctrl+C" → EXECUTE: press_key("ctrl+c")

Always be helpful and explain what you're doing. If you need clarification about a command, ask the user and keep the responses brief and friendly assume the os is windows."""

    def parse_and_execute_command(self, llm_response):
        """Parse LLM response and execute any commands"""
        results = []
        
        # Look for EXECUTE: commands in the response
        execute_pattern = r'EXECUTE:\s*(\w+)\((.*?)\)'
        matches = re.findall(execute_pattern, llm_response)
        
        for function_name, params_str in matches:
            try:
                # Parse parameters
                if params_str.strip():
                    # Handle string parameters with quotes
                    params = []
                    current_param = ""
                    in_quotes = False
                    quote_char = None
                    
                    i = 0
                    while i < len(params_str):
                        char = params_str[i]
                        
                        if char in ['"', "'"] and not in_quotes:
                            in_quotes = True
                            quote_char = char
                        elif char == quote_char and in_quotes:
                            in_quotes = False
                            quote_char = None
                            params.append(current_param)
                            current_param = ""
                        elif char == ',' and not in_quotes:
                            if current_param.strip():
                                # Try to convert to int if it's a number
                                param = current_param.strip()
                                try:
                                    param = int(param)
                                except ValueError:
                                    pass
                                params.append(param)
                            current_param = ""
                        elif in_quotes or char != ' ':
                            current_param += char
                        
                        i += 1
                    
                    # Add the last parameter
                    if current_param.strip():
                        param = current_param.strip()
                        try:
                            param = int(param)
                        except ValueError:
                            pass
                        params.append(param)
                else:
                    params = []
                
                # Execute the command
                if hasattr(self.commands, function_name):
                    function = getattr(self.commands, function_name)
                    result = function(*params)
                    results.append(f"✓ {function_name}: {result}")
                else:
                    results.append(f"✗ Unknown command: {function_name}")
                    
            except Exception as e:
                results.append(f"✗ Error executing {function_name}: {str(e)}")
        
        return results

    def get_llm_response(self, user_input, conversation_history=""):
        import google.generativeai as genai
        
        # Configure the API key
        genai.configure(api_key="AIzaSyC8aZFiK66R_mmhQTy7iHE9dSh4nM7b6AM")
        
        # Create the model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=self.system_prompt
        )
        
        # Prepare the full prompt
        full_prompt = f"{conversation_history}\nUser: {user_input}\nAssistant:"
        
        # Generate content
        response = model.generate_content(full_prompt)
        
        return response.text
    
        """
        try:
            # Prepare the full prompt
            full_prompt = f"{conversation_history}\nUser: {user_input}\nAssistant:"
            
            input_data = {
                "prompt": full_prompt,
                "system_prompt": self.system_prompt,
                "max_tokens": 1024,
                "temperature": 0.7
            }
            
            # Stream the response
            response = ""
            for event in replicate.stream("anthropic/claude-4-sonnet", input=input_data):
                response += str(event)
            
            return response
            
        except Exception as e:
            return f"Error getting LLM response: {str(e)}"
        """

    def process_message(self, user_message, conversation_history=""):
        """Process a message and execute commands directly"""
        try:
            if not user_message.strip():
                return {
                    'error': 'No message provided',
                    'status': 'error'
                }
            
            # Handle special commands
            if user_message.lower() == 'help':
                help_text = """Available Commands (examples):
• "Open Chrome" / "Open Notepad"
• "Close Chrome" / "Minimize window"  
• "Create a file called test.txt"
• "Open google.com"
• "Take a screenshot"
• "Press Ctrl+C"
• "Type hello world"
• "List files in current directory"
• "What applications are running?"

Just speak naturally - I'll understand what you want to do!"""
                
                return {
                    'user_message': user_message,
                    'bot_response': help_text,
                    'command_results': [],
                    'status': 'success'
                }
            
            # Get LLM response
            llm_response = self.get_llm_response(user_message, conversation_history)
            
            # Execute commands immediately
            command_results = self.parse_and_execute_command(llm_response)
            
            return {
                'user_message': user_message,
                'bot_response': llm_response,
                'command_results': command_results,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'error': f'Processing error: {str(e)}',
                'status': 'error'
            }

# Global chatbot instance and conversation history
chatbot = AccessibilityChatbot()
conversation_history = ""

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message(input_message=None):
    """Handle incoming messages and execute commands directly"""
    global conversation_history
    
    try:
        if input_message:
            user_message = input_message.strip()
        else:
            data = request.get_json()
            user_message = data.get('message', '').strip()
        
        # Process the message using the chatbot
        result = chatbot.process_message(user_message, conversation_history)
        
        # Update conversation history if successful
        if result['status'] == 'success' and 'bot_response' in result:
            conversation_history += f"\nUser: {user_message}\nAssistant: {result['bot_response']}"
            history_lines = conversation_history.split('\n')
            if len(history_lines) > 20:
                conversation_history = '\n'.join(history_lines[-20:])
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/quick_command', methods=['POST'])
def quick_command():
    """Handle quick command buttons"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        # Process as regular message
        return send_message(command)
        
    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/status')
def get_status():
    """Get server status"""
    try:
        # Test if chatbot is working
        test_response = chatbot.get_llm_response("test", "")

        return jsonify({
            'status': 'ready',
            'message': '🟢 Connected',
            'chatbot_initialized': True
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'🔴 Error: {str(e)}',
            'chatbot_initialized': False
        })

@app.route('/voice_toggle', methods=['POST'])
def voice_toggle():
    """Handle voice button toggle"""
    try:
        data = request.get_json()
        action = data.get('action', '').strip()
        
        if action == 'start':
            chatbot.voice_recognition.start_voice()
            print("🎤 Voice button pressed - Starting voice recognition!")
            print("📢 User wants to use voice input")
            print("🔊 This is where you would initialize speech recognition")
            
            return jsonify({
                'status': 'success',
                'message': 'Voice recognition started',
                'action': 'start'
            })
            
        elif action == 'stop':
            chatbot.voice_recognition.stop_voice()
            # Instead of hardcoded "open chrome", you might want to get the actual voice input
            result = chatbot.process_message("open chrome", conversation_history)
            print("🛑 Voice button pressed - Stopping voice recognition!")
            print("🔇 Voice recognition stopped by user")
            print("✅ Voice session ended")
            
            return jsonify(result)
        else:
            print(f"❓ Unknown voice action: {action}")
            return jsonify({
                'status': 'error',
                'message': 'Unknown action'
            }), 400
            
    except Exception as e:
        print(f"❌ Voice toggle error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Voice error: {str(e)}'
        }), 500

class GlowOverlay(QtWidgets.QWidget):
    """PyQt overlay widget for visual feedback"""
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool  # Does not appear in taskbar
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        screen = QtWidgets.QApplication.primaryScreen()
        size = screen.size()

        # Set the overlay window geometry at the bottom of the screen
        glow_height = 50
        self.setGeometry(0, size.height() - glow_height, size.width(), glow_height)

        self.showing = False

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        color = QtGui.QColor(0, 150, 100, 150)  # Semi-transparent blue
        glow = QtGui.QRadialGradient(self.width() // 2, 0, self.width())
        glow.setColorAt(0, color)
        glow.setColorAt(1, QtCore.Qt.transparent)
        painter.setBrush(glow)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(self.rect())

    def toggle(self):
        if self.showing:
            self.hide()
            self.showing = False
        else:
            self.show()
            self.showing = True

class HotkeyManager:
    """Manages hotkeys in a separate thread"""
    def __init__(self, chatbot_instance, overlay_widget=None):
        self.chatbot = chatbot_instance
        self.overlay = overlay_widget
        self.voice_active = False
        self.conversation_history = ""
        self._stop_event = threading.Event()
        
    def start(self):
        """Start the hotkey manager in a separate thread"""
        self.hotkey_thread = threading.Thread(target=self._run_hotkey_loop, daemon=True)
        self.hotkey_thread.start()
        print("🎯 Hotkey manager started in separate thread")
        
    def stop(self):
        """Stop the hotkey manager"""
        self._stop_event.set()
        keyboard.unhook_all()
        print("🛑 Hotkey manager stopped")
    
    def _run_hotkey_loop(self):
        """Run the hotkey listener loop"""
        try:
            # Register hotkey
            keyboard.add_hotkey('alt+v', self._toggle_voice)
            print("🎯 Hotkey registered: Alt+V to toggle voice")
            
            # Keep the thread alive until stop is requested
            while not self._stop_event.is_set():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"❌ Hotkey thread error: {str(e)}")
    
    def _toggle_voice(self):
        """Toggle voice recognition via hotkey and process commands directly"""
        try:
            if not self.voice_active:
                # Start voice recognition
                self.chatbot.voice_recognition.start_voice()
                self.voice_active = True
                print("🎤 Hotkey triggered - Voice recognition STARTED")
                print("📢 Listening for voice input...")
                
                # Show overlay if available
                if self.overlay:
                    self.overlay.show()
                    self.overlay.showing = True
                
            else:
                # Stop voice recognition and process command
                command_text = self.chatbot.voice_recognition.stop_voice()
                self.voice_active = False
                print("🛑 Hotkey triggered - Voice recognition STOPPED")
                
                # Hide overlay if available
                if self.overlay:
                    self.overlay.hide()
                    self.overlay.showing = False
                #speak(f"🎯 Processing voice command: {command_text}")
                
                # Process the message directly using the chatbot
                result = self.chatbot.process_message(command_text, self.conversation_history)
                
                speak(result['bot_response'].split('\n')[0])  # Speak the first line of the response

                # Update conversation history
                if result['status'] == 'success' and 'bot_response' in result:
                    self.conversation_history += f"\nUser: {command_text}\nAssistant: {result['bot_response']}"
                    history_lines = self.conversation_history.split('\n')
                    if len(history_lines) > 20:
                        self.conversation_history = '\n'.join(history_lines[-20:])
                
                # Print results
                print(f"✅ Command processed: {result['status']}")
                if 'command_results' in result:
                    for cmd_result in result['command_results']:
                        print(f"   {cmd_result}")
                
                if result['status'] == 'error':
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
                    
        except Exception as e:
            print(f"❌ Hotkey error: {str(e)}")
            self.voice_active = False

class AccessibilityApp:
    """Main application class that coordinates all components"""
    
    def __init__(self):
        self.chatbot = chatbot
        self.flask_thread = None
        self.hotkey_manager = None
        self.qt_app = None
        self.overlay = None
        
    def start_flask_server(self):
        """Start Flask server in a separate thread"""
        def run_flask():
            try:
                # Disable Flask reloader and run in non-debug mode for threading
                app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False, threaded=True)
            except Exception as e:
                print(f"❌ Flask server error: {str(e)}")
        
        self.flask_thread = threading.Thread(target=run_flask, daemon=True)
        self.flask_thread.start()
        print("🌐 Flask server started in separate thread")
        
    def start_qt_app(self):
        """Initialize and start PyQt application"""
        try:
            # Create QApplication
            self.qt_app = QtWidgets.QApplication(sys.argv)
            
            # Create overlay widget
            self.overlay = GlowOverlay()
            
            print("🎨 PyQt application initialized")
            return True
            
        except Exception as e:
            print(f"❌ PyQt initialization error: {str(e)}")
            return False
            
    def start_hotkey_manager(self):
        """Start hotkey manager"""
        try:
            self.hotkey_manager = HotkeyManager(self.chatbot, self.overlay)
            self.hotkey_manager.start()
            print("⌨️ Hotkey manager started")
            
        except Exception as e:
            print(f"❌ Hotkey manager error: {str(e)}")
            
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
            self.shutdown()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def shutdown(self):
        """Gracefully shutdown all components"""
        print("🛑 Shutting down accessibility app...")
        
        if self.hotkey_manager:
            self.hotkey_manager.stop()
            
        if self.qt_app:
            self.qt_app.quit()
            
        print("✅ Shutdown complete")
        
    def run(self):
        """Main entry point - start all components"""
        print("🚀 Starting Accessibility Assistant...")
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Start Flask server
        self.start_flask_server()
        
        # Start PyQt application
        if not self.start_qt_app():
            print("❌ Failed to start PyQt application")
            return
            
        # Start hotkey manager
        self.start_hotkey_manager()
        
        # Print status
        print("🌐 Web server: http://localhost:5000")
        print("🎯 Global Hotkey: Alt+V (toggle voice)")
        print("🎨 Visual overlay active")
        print("✅ All components started successfully!")
        
        # Run Qt event loop (this blocks the main thread)
        try:
            sys.exit(self.qt_app.exec_())
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
            self.shutdown()

if __name__ == '__main__':
    app_instance = AccessibilityApp()
    app_instance.run()