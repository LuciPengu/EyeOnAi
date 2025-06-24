import replicate
import json
import re
import os
from computer_commands import AccessibilityCommands

class AccessibilityChatbot:
    def __init__(self):
        """Initialize the chatbot with Replicate API token"""
        self.commands = AccessibilityCommands()
        
        # Set API token directly in the environment
        os.environ["REPLICATE_API_TOKEN"] = "r8_UqTVSqvFhzR8pAyBHFVSsLShg0c3Pjr0A5n2q"
        
        # Initialize replicate client
        replicate.api_token = os.environ["REPLICATE_API_TOKEN"]
        aefawefawef
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

Always be helpful and explain what you're doing. If you need clarification about a command, ask the user."""

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
        """Get response from Replicate LLM"""
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

    def chat(self):
        """Main chat loop"""
        print("🤖 Accessibility Chatbot Started!")
        print("Type 'exit' to quit, 'help' for available commands")
        print("-" * 50)
        
        conversation_history = ""
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() == 'exit':
                    print("🤖 Goodbye! Cleaning up...")
                    self.commands.cleanup()
                    break
                
                if user_input.lower() == 'help':
                    print("""
🤖 Available Commands (examples):
• "Open Chrome" / "Open Notepad"
• "Close Chrome" / "Minimize window"
• "Create a file called test.txt"
• "Open google.com"
• "Take a screenshot"
• "Press Ctrl+C"
• "Type hello world"
• "List files in current directory"
• "What applications are running?"
                    """)
                    continue
                
                if not user_input:
                    continue
                
                # Get LLM response
                print("🤖 Assistant: ", end="", flush=True)
                llm_response = self.get_llm_response(user_input, conversation_history)
                print(llm_response)
                
                # Execute any commands found in the response
                command_results = self.parse_and_execute_command(llm_response)
                
                if command_results:
                    print("\n📋 Command Results:")
                    for result in command_results:
                        print(f"  {result}")
                
                # Update conversation history (keep last 5 exchanges)
                conversation_history += f"\nUser: {user_input}\nAssistant: {llm_response}"
                history_lines = conversation_history.split('\n')
                if len(history_lines) > 20:  # Keep last 10 exchanges (20 lines)
                    conversation_history = '\n'.join(history_lines[-20:])
                
            except KeyboardInterrupt:
                print("\n🤖 Goodbye! Cleaning up...")
                self.commands.cleanup()
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

def main():
    """Main function to start the chatbot"""
    print("🚀 Starting Accessibility Chatbot...")
    
    try:
        # Initialize and start chatbot
        chatbot = AccessibilityChatbot()
        chatbot.chat()
    except Exception as e:
        print(f"❌ Error initializing chatbot: {str(e)}")
        return

if __name__ == "__main__":
    main()
