import js
import asyncio
import json
from js import document
from pyodide.http import pyfetch

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

    if not speech_recognition_active:
        update_info("Listening for speech...")
        speech_recognition_active = True
        try:
            transcribed_text = await js.window.startSpeechRecognition()
            
            speech_recognition_active = False
            if transcribed_text:
                update_info(f"You said: '{transcribed_text}'")                
                user_input_field = js.document.getElementById('userInput')
                if user_input_field:
                    user_input_field.value = transcribed_text
                    # js.sendMessage() 
                    await py_sendMessage()
                
            else:
                update_info("No speech detected or unclear.")
                print("Python: No speech detected.")

        except Exception as e:
            speech_recognition_active = False 
            error_message = f"Speech recognition error: {e}"
            update_info(error_message)
            print(f"Python Error: {error_message}")
    else:
        update_info("Stopping listening...")
        print("Python: Stopping speech recognition...")
        js.window.stopSpeechRecognition() 
        speech_recognition_active = False
        update_info("Listening stopped.")

# def scroll_to_bottom():
#     chat_messages_container = js.document.getElementById('chatMessages')
#     # Scroll to the bottom using scrollTop and scrollHeight
#     chat_messages_container.scrollTop = chat_messages_container.scrollHeight

# For chatbot
async def get_bot_response(user_message):
    if not user_message.strip():
        return "Please enter something."

    try:
        response = await pyfetch(
            url="/get-response",
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"message": user_message})
        )
        data = await response.json()
        return data.get("response", "No response from chatbot.")
    except Exception as e:
        return f"Error talking to server: {str(e)}"

# # When send button is clicked
# async def get_bot_response(user_message):
#     try:
#         with open("chatbot_data.json", "r") as f:
#             data = json.load(f)

#         questions = [q["question"] for q in data]
#         answers = [q["answer"] for q in data]

#         vectorizer = TfidfVectorizer()
#         X = vectorizer.fit_transform(questions + [user_message])
#         similarity = cosine_similarity(X[-1], X[:-1])

#         best_match_idx = similarity.argmax()
#         best_score = similarity[0, best_match_idx]

#         if best_score >= 0.6:
#             bot_reply = answers[best_match_idx]
#         else:
#             user_lower = user_message.lower()
#             if "hello" in user_lower or "hi" in user_lower:
#                 bot_reply = "Hello there! How can I assist you today?"
#             elif "time" in user_lower:
#                 bot_reply = "It's currently 3:55 PM IST in Surat, Gujarat."
#             elif "name" in user_lower or "who are you" in user_lower:
#                 bot_reply = "I am VID-Assistant, your virtual interactive digital assistant."
#             elif "help" in user_lower:
#                 bot_reply = "I can help you with various tasks. Just ask!"
#             else:
#                 bot_reply = "Sorry, I am unable to answer this question."

#         await asyncio.sleep(0.3)
#         return bot_reply

#     except Exception as e:
#         print(f"Error: {e}")
#         return "Oops! Something went wrong."

current_audio = None
def play_audio(audio_file_path, event=None):
    global current_audio

    if current_audio is not None:
        current_audio.pause()
        current_audio.currentTime = 0 

    audio = js.Audio.new(audio_file_path)
    audio.play()
    current_audio = audio 


async def py_sendMessage(event=None):
    """
    Handles sending and displaying chat messages in the chat interface,
    and gets a bot response which is then spoken in audio.
    """

    if event is not None:
        event.preventDefault()

    input_element = js.document.getElementById('userInput')
    message = input_element.value.strip()

    if message == "":
        return

    chat_messages_container = js.document.getElementById('chatMessages')

    user_message_div = js.document.createElement('div')
    user_text_p = js.document.createElement('p')
    user_text_p.innerText = message
    user_text_p.className = 'user-message'
    user_message_div.appendChild(user_text_p)
    chat_messages_container.appendChild(user_message_div)
    input_element.value = '' 
    user_message_div.scrollIntoView({'behavior': 'smooth'})
    bot_reply_text = await get_bot_response(message)

    # mic_button.onclick = play_audio()

    if bot_reply_text:
        bot_message_div = js.document.createElement('div')
        bot_message_div.className = 'bot-message-container' 

        bot_text_p = js.document.createElement('p')
        bot_text_p.innerText = bot_reply_text
        bot_text_p.className = 'bot-message'
        bot_message_div.appendChild(bot_text_p)

        mic_button = js.document.createElement('button')
        mic_button.className = 'mic-button'
        mic_image = js.document.createElement('img')
        mic_image.src = '../static/images/speack-btn.png'
        mic_image.className = 'mic-icon-image'
        mic_button.appendChild(mic_image)
        bot_message_div.appendChild(mic_button)
        chat_messages_container.appendChild(bot_message_div)
        
        # scroll_to_bottom()
        bot_message_div.scrollIntoView({'behavior': 'smooth'})
        audio_path = await play_bot_speech(bot_reply_text)
        if audio_path: 
            mic_button.setAttribute('data-audio-path', audio_path)
            mic_button.onclick = lambda event: play_audio(event.currentTarget.getAttribute('data-audio-path'))


async def play_bot_speech(text_to_speak):
    try:
        my_headers = js.Headers.new()
        my_headers.append("Content-Type", "application/json")
        response = await js.fetch(
            "/synthesize-speech",method= "POST",headers=my_headers,body=json.dumps({"text": text_to_speak})
            )
        if response.ok:
            audio_file_path = await response.text()            
            print(f"frontend: {audio_file_path}")
            play_audio(audio_file_path)
            return audio_file_path

        else:
            error_text = await response.text() 
            print(f"PyScript Response: Error Body: {error_text}")
            print(f"Python Error: TTS request failed with status {response.status}. Response: {error_text}")
            update_info(f"TTS Error: Status {response.status}")
    except Exception as e:
        print(f"Python Exception while requesting/playing TTS audio: {e}")
        update_info(f"Audio playback error: {e}")

async def main_pyscript_init():
    mic_button = js.document.getElementById('micButton')
    send_button = js.document.getElementById('sendButton') 
    user_input = js.document.getElementById('userInput')
    if mic_button and send_button:
        mic_button.onclick = handle_mic_click 
        send_button.onclick = lambda event: asyncio.ensure_future(py_sendMessage(event))
        user_input.onkeyup = lambda event: asyncio.ensure_future(py_sendMessage()) if event.key == 'Enter' else None
    else:
        update_info("Error: Mic button not found for PyScript control.")
    print("Python: PyScript main initialization complete.")


# Ensure the main PyScript initialization runs
asyncio.ensure_future(main_pyscript_init())
