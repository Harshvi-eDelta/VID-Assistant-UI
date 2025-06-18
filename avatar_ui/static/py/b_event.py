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


# Main initialization for PyScript
async def main_pyscript_init():
    mic_button = js.document.getElementById('micButton')
    if mic_button:
        mic_button.onclick = handle_mic_click 
        # print("PyScript initialized. Click mic to speak.")
        update_info("PyScript initialized. Click mic to speak.")
    else:
        update_info("Error: Mic button not found for PyScript control.")
    print("Python: PyScript main initialization complete.")

# Ensure the main PyScript initialization runs
asyncio.ensure_future(main_pyscript_init())