# static/py/app.py

import js
import asyncio

# Global state for speech recognition
speech_recognition_active = False

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
                    # You might want to automatically send the message here too
                    # js.sendMessage() # If sendMessage is a global JS function
                
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

async def py_sendMessage(event=None): # event=None to accept JS event object if passed
    """
    Handles sending and displaying chat messages in the chat interface.
    This function replaces the original JavaScript sendMessage.
    """
    input_element = js.document.getElementById('userInput')
    message = input_element.value.strip()

    if message != "":
        chat_messages_container = js.document.getElementById('chatMessages')

        # User message
        user_message_div = js.document.createElement('div')
        user_text_p = js.document.createElement('p')
        user_text_p.innerText = message
        user_text_p.className = 'user-message' # Note: No leading/trailing space needed for single class
        user_message_div.appendChild(user_text_p)
        chat_messages_container.appendChild(user_message_div)

        input_element.value = '' # Clear input
        # smooth_scroll_to_bottom(chat_messages_container)
        print("create msg")
        # Bot reply (simulated with a delay)
        await asyncio.sleep(0.5) # Equivalent to setTimeout(..., 500)

        bot_message_div = js.document.createElement('div')
        # bot_message_div.className = 'message' # You might not need this if p tag has enough styling
        bot_text_p = js.document.createElement('p')
        bot_text_p.innerText = message 
        bot_text_p.className = 'bot-message'
        bot_message_div.appendChild(bot_text_p)
        chat_messages_container.appendChild(bot_message_div)
        
        # smooth_scroll_to_bottom(chat_messages_container)


# Main initialization for PyScript
async def main_pyscript_init():
    mic_button = js.document.getElementById('micButton')
    send_button = js.document.getElementById('sendButton') 
    print(send_button)
    if mic_button and send_button:
        mic_button.onclick = handle_mic_click 
        send_button.onclick = py_sendMessage
        # print("PyScript initialized. Click mic to speak.")
        update_info("PyScript initialized. Click mic to speak.")
    else:
        update_info("Error: Mic button not found for PyScript control.")
    print("Python: PyScript main initialization complete.")
    # js.window.py_sendMessage = py_sendMessage
    # print("Python: py_sendMessage exposed to JS.")

# Ensure the main PyScript initialization runs
asyncio.ensure_future(main_pyscript_init())