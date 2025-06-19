import js
import asyncio

# Global state for speech recognition
speech_recognition_active = False
current_py_utterance = None

def update_info(message):
    """Helper function to update the info div in HTML."""
    info_div = js.document.getElementById('info')
    if info_div:
        info_div.textContent = message
    else:
        print(f"Python Warning: Could not find #info div. Message: {message}")

async def handle_mic_click(event=None):
    """
    Handles the mic button click event to start/stop speech recognition.
    """
    global speech_recognition_active

    # if not js.window.SpeechRecognition and not js.window.webkitSpeechRecognition:
    #     update_info("Speech Recognition not supported in this browser.")
    #     print("Python: Speech Recognition not supported in this browser.")
    #     return

    if not speech_recognition_active:
        update_info("Listening for speech...")
        print("Python: Starting speech recognition...")
        speech_recognition_active = True
        try:
            # Call the JavaScript function to start recognition
            # Await the result of the Promise returned by the JS function
            transcribed_text = await js.window.startSpeechRecognition()
            
            speech_recognition_active = False # Reset state after recognition
            if transcribed_text:
                update_info(f"You said: '{transcribed_text}'")
                print(f"Python: Transcribed text: '{transcribed_text}'")
                
                # Optionally, send the transcribed text to the chat input
                user_input_field = js.document.getElementById('userInput')
                if user_input_field:
                    user_input_field.value = transcribed_text
                    # print("py: auto send")
                    # You might want to automatically send the message here too
                    # js.sendMessage() # If sendMessage is a global JS function
                    await py_sendMessage()
                
            else:
                update_info("No speech detected or unclear.")
                print("Python: No speech detected.")

        except Exception as e:
            speech_recognition_active = False # Reset state on error
            error_message = f"Speech recognition error: {e}"
            update_info(error_message)
            print(f"Python Error: {error_message}")
    else:
        # If recognition is already active, stop it (optional, as `continuous` is false)
        update_info("Stopping listening...")
        print("Python: Stopping speech recognition...")
        js.window.stopSpeechRecognition() # Call JS function to stop
        speech_recognition_active = False
        update_info("Listening stopped.")


def smooth_scroll_to_bottom(element):
    """Calls the JavaScript smoothScrollToBottom function."""
    js.window.smoothScrollToBottom(element) # Call the JS function

async def get_bot_response(user_message):
    """
    Simulates getting a response from a bot.
    In a real application, this would involve an HTTP request to a backend API.
    For now, a simple conditional response.
    """
    print(f"Python: Getting bot response for: '{user_message}'")
    # Replace this with an actual API call to your backend
    # Example using pyfetch (PyScript's fetch API wrapper):
    try:
        # Assuming you have a Flask backend running at /api/chat
        # response = await pyfetch("/api/chat", method='POST',
        #                          headers={'Content-Type': 'application/json'},
        #                          body=js.JSON.stringify({'message': user_message}))
        # if response.ok:
        #     data = await response.json()
        #     bot_reply = data.get('response', 'Sorry, I could not get a response.')
        # else:
        #     bot_reply = f"Error: {response.status} {await response.text()}"

        # Simple static response for demonstration
        if "hello" in user_message.lower() or "hi" in user_message.lower():
            bot_reply = "Hello there! How can I assist you today?"
        elif "time" in user_message.lower():
            bot_reply = "I'm a virtual assistant, I don't have a concept of time, but I can tell you the current time is 3:55 PM IST, June 19, 2025 in Surat, Gujarat, India."
        elif "name" in user_message.lower():
            bot_reply = "I am VID-Assistant, your virtual interactive digital assistant."
        elif "who are you" in user_message.lower():
            bot_reply = "I am VID-Assistant, your virtual interactive digital assistant. I can help you with your queries."
        elif "help" in user_message.lower():
            bot_reply = "I can help you with various tasks, just ask me anything!"
        else:
            bot_reply = f"You asked: '{user_message}'. now i don't understand what are u saying. How else can I help?"
        await asyncio.sleep(0.5) # Simulate network delay
        return bot_reply
    except Exception as e:
        print(f"Python Error fetching bot response: {e}")
        return "I'm sorry, I encountered an error while trying to respond."

def py_speak_text(text):
    global current_py_utterance # Declare global here to access/modify the module-level variable

    if not text or text.strip() == '':
        print('Python TTS: Attempted to speak empty or null text.')
        return

    if not hasattr(js.window, 'speechSynthesis'):
        print('Python TTS: Text-to-Speech not supported in this browser.')
        update_info('Text-to-Speech not supported in your browser.')
        return

    # Cancel any currently speaking utterance
    if current_py_utterance and js.window.speechSynthesis.speaking:
        js.window.speechSynthesis.cancel()

    utterance = js.new(js.window.SpeechSynthesisUtterance, text)
    utterance.lang = 'en-US'

    def on_end(e):
        print('Python TTS: Speech synthesis finished.')
        global current_py_utterance # Declare global here too, as it modifies it
        current_py_utterance = None
    utterance.onend = on_end

    def on_error(e):
        print(f'Python TTS: Speech synthesis error: {e.error}')
        global current_py_utterance # Declare global here too, as it modifies it
        current_py_utterance = None
    utterance.onerror = on_error

    js.window.speechSynthesis.speak(utterance)
    current_py_utterance = utterance # Store reference
    print(f'Python TTS: Speaking: "{text}"')


async def py_sendMessage(event=None): # event=None to accept JS event object if passed
    """
    Handles sending and displaying chat messages in the chat interface,
    and gets a bot response which is then spoken in audio.
    """
    input_element = js.document.getElementById('userInput')
    message = input_element.value.strip()

    if message == "":
        return # Do nothing if message is empty

    chat_messages_container = js.document.getElementById('chatMessages')

    # 1. Display User message
    user_message_div = js.document.createElement('div')
    user_text_p = js.document.createElement('p')
    user_text_p.innerText = message
    user_text_p.className = 'user-message'
    user_message_div.appendChild(user_text_p)
    chat_messages_container.appendChild(user_message_div)

    input_element.value = '' # Clear input after sending
    # js.window.smoothScrollToBottom(chat_messages_container) # Scroll after adding user message

    # 2. Get Bot Response
    bot_reply_text = await get_bot_response(message)
    print(f"Python: Bot response received: '{bot_reply_text}'")

    # 3. Display Bot Response
    bot_message_div = js.document.createElement('div')
    bot_text_p = js.document.createElement('p')
    bot_text_p.innerText = bot_reply_text
    bot_text_p.className = 'bot-message'
    bot_message_div.appendChild(bot_text_p)
    chat_messages_container.appendChild(bot_message_div)

    # js.window.smoothScrollToBottom(chat_messages_container) # Scroll after adding bot message

    # 4. Speak Response in Audio
    if bot_reply_text:
        print(f"Python: Calling internal py_speak_text to speak: '{bot_reply_text}'")
        py_speak_text(bot_reply_text) # <<< CALLING THE NEW PYTHON TTS FUNCTION
    else:
        print("Python: Bot response was empty, nothing to speak.")



# Main initialization for PyScript
async def main_pyscript_init():
    mic_button = js.document.getElementById('micButton')
    send_button = js.document.getElementById('sendButton') 
    user_input = js.document.getElementById('userInput') # Get the input field
    print(send_button)
    if mic_button and send_button:
        mic_button.onclick = handle_mic_click 
        send_button.onclick = py_sendMessage
        user_input.onkeyup = lambda event: asyncio.ensure_future(py_sendMessage()) if event.key == 'Enter' else None
        # print("PyScript initialized. Click mic to speak.")
        update_info("PyScript initialized. Click mic to speak.")
    else:
        update_info("Error: Mic button not found for PyScript control.")
    print("Python: PyScript main initialization complete.")
    # js.window.py_sendMessage = py_sendMessage
    # print("Python: py_sendMessage exposed to JS.")

# Ensure the main PyScript initialization runs
asyncio.ensure_future(main_pyscript_init())