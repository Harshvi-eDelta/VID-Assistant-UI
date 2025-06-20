import datetime
start = datetime.datetime.now()
import tensorflow as tf
import numpy as np
import librosa
import soundfile as sf
import io
import os
from text_preprocess import TextNormalizer
from hybrid_G2P import G2PConverter
# Important: Register custom Keras layers before loading the model
# Keras needs to know how to deserialize these custom layers.
# The `register_keras_serializable()` decorator should be at the class definition.
# If you didn't define them in this file, you'd need to import them from where they are defined.
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras import layers
from keras.saving import register_keras_serializable
from keras.config import enable_unsafe_deserialization
enable_unsafe_deserialization()

# --- Custom Keras Layers (Copy them directly here or import from a shared utility file) ---
# It's crucial that these definitions are available when you load the model.
# If these layers are defined in `your_project_root/acoustic/text_preprocess.py`
# then you should import them directly from there.
# For simplicity, I'm assuming you'll put them here or ensure they are loaded.


@register_keras_serializable()
class CropLayer(tf.keras.layers.Layer):
    def __init__(self, length, **kwargs):
        super().__init__(**kwargs)
        self.length = length

    def call(self, inputs):
        return inputs[:, :self.length, :]

    def get_config(self):
        config = super().get_config()
        config.update({'length': self.length})
        return config
    
@register_keras_serializable()
class AdditiveAttention(tf.keras.layers.Layer):
    def __init__(self, units, **kwargs):
        super(AdditiveAttention, self).__init__(**kwargs)
        self.W_query = tf.keras.layers.Dense(units)
        self.W_values = tf.keras.layers.Dense(units)
        self.V = tf.keras.layers.Dense(1)

    def call(self, query, values, mask=None):
        query = tf.expand_dims(query, 1)
        score = self.V(tf.nn.tanh(self.W_query(query) + self.W_values(values)))
        score = tf.squeeze(score, axis=-1)

        if mask is not None:
            score += (1.0 - tf.cast(mask, tf.float32)) * -1e9

        attention_weights = tf.nn.softmax(score, axis=-1)
        context = tf.matmul(tf.expand_dims(attention_weights, 1), values)
        context = tf.squeeze(context, axis=1)
        return context, attention_weights

@register_keras_serializable()
class AttentionContextLayer(tf.keras.layers.Layer):
    def __init__(self, units, input_length, **kwargs):
        super(AttentionContextLayer, self).__init__(**kwargs)
        self.units = units
        self.input_length = input_length

    def build(self, input_shape):
        self.attention = AdditiveAttention(units=self.units)
        super(AttentionContextLayer, self).build(input_shape)

    def call(self, inputs):
        query, values, mask = inputs
        context_vector, _ = self.attention(query, values, mask=mask)
        
        # Expand context and concatenate with sequence
        context_expanded = tf.expand_dims(context_vector, axis=1)
        context_expanded = tf.tile(context_expanded, [1, self.input_length, 1])
        return tf.concat([values, context_expanded], axis=-1)

@register_keras_serializable()
class LocationSensitiveAttention(tf.keras.layers.Layer):
    def __init__(self, units, filters=32, kernel_size=31, **kwargs):
        super(LocationSensitiveAttention, self).__init__(**kwargs)
        self.units = units
        self.filters = filters
        self.kernel_size = kernel_size
        self.W_query = layers.Dense(units)
        self.W_values = layers.Dense(units)
        self.W_location = layers.Dense(units)
        self.V = layers.Dense(1)
        self.location_conv = layers.Conv1D(filters, kernel_size, padding='same', use_bias=False)

    def call(self, query, values, prev_attention, mask=None):
        # prev_attention: (batch_size, seq_len)
        query = tf.expand_dims(query, 1)  # (batch_size, 1, dim)

        # Location features
        f = self.location_conv(tf.expand_dims(prev_attention, -1))  # (batch_size, seq_len, filters)
        location_features = self.W_location(f)

        # Score calculation
        score = self.V(tf.nn.tanh(
            self.W_query(query) + self.W_values(values) + location_features))  # (batch, seq_len, 1)
        score = tf.squeeze(score, -1)

        if mask is not None:
            score += (1.0 - tf.cast(mask, tf.float32)) * -1e9

        attention_weights = tf.nn.softmax(score, axis=-1)
        context_vector = tf.matmul(tf.expand_dims(attention_weights, 1), values)
        context_vector = tf.squeeze(context_vector, axis=1)

        return context_vector, attention_weights

@register_keras_serializable()
class LocationAttentionContextLayer(tf.keras.layers.Layer):
    def __init__(self, units, input_length, **kwargs):
        super(LocationAttentionContextLayer, self).__init__(**kwargs)
        self.units = units
        self.input_length = input_length

    def build(self, input_shape):
        self.attention = LocationSensitiveAttention(units=self.units)
        super().build(input_shape)

    def call(self, inputs):
        query, values, prev_attention, mask = inputs
        context_vector, attention_weights = self.attention(query, values, prev_attention, mask=mask)
        context_expanded = tf.expand_dims(context_vector, axis=1)
        context_expanded = tf.tile(context_expanded, [1, self.input_length, 1])
        return tf.concat([values, context_expanded], axis=-1), attention_weights

@tf.keras.utils.register_keras_serializable()
class PositionalEncoding(tf.keras.layers.Layer):
    def __init__(self, input_length, embed_dim, **kwargs):
        super(PositionalEncoding, self).__init__(**kwargs)
        self.pos_embedding = tf.keras.layers.Embedding(input_dim=input_length, output_dim=embed_dim)

    def call(self, x):
        seq_len = tf.shape(x)[1]
        positions = tf.range(start=0, limit=seq_len, delta=1)
        positions = tf.expand_dims(positions, 0)
        pos_encoded = self.pos_embedding(positions)
        return pos_encoded

@tf.keras.utils.register_keras_serializable()
class LastTimestep(tf.keras.layers.Layer):
    def call(self, inputs):
        return inputs[:, -1, :]

class CustomTTS:
    def __init__(self):
        self.best_model = None
        self.g2p = None
        self.normalizer = None
        self.mel_mean = None
        self.mel_std = None
        self.is_loaded = False
        self._load_models() # Load models during initialization

    def _load_models(self):
        """Loads all necessary models and data."""
        try:
            # Ensure custom objects are passed for model loading
            custom_objects = {
                'CropLayer': CropLayer,
                'AdditiveAttention': AdditiveAttention,
                'AttentionContextLayer': AttentionContextLayer,
                'LocationSensitiveAttention': LocationSensitiveAttention,
                'LocationAttentionContextLayer': LocationAttentionContextLayer,
                'PositionalEncoding': PositionalEncoding,
                'LastTimestep': LastTimestep,
            }

            # print(os.path.join(os.path.dirname(__file__), "models/1best_model_cnn_r_EarlyStopping.keras"))            
            self.best_model = tf.keras.models.load_model(
                os.path.join(os.path.dirname(__file__), "models/1best_model_cnn_r_EarlyStopping.keras"),
                compile=False,
                custom_objects=custom_objects
            )
            print("TTS: Keras TTS model loaded.")

            self.g2p = G2PConverter("avatar_ui/TTS_pipeline/models/3model_cnn.keras")            
            print("TTS: G2P model loaded.")

            self.normalizer = TextNormalizer()
            print("TTS: TextNormalizer initialized.")

            mean_std_path = os.path.join(
                os.path.dirname(__file__),
                "data/acoustic_dataset/mel_mean_std.npy"
            )
            self.mel_mean, self.mel_std = np.load(mean_std_path)
            print("TTS: Mel mean/std loaded.")

            self.is_loaded = True
            print("TTS: All models and data loaded successfully!")
        except Exception as e:
            self.is_loaded = False
            print(f"TTS Error: Failed to load models: {e}")
            # Re-raise the exception or handle appropriately if you want Flask to show an error

    def mel_to_audio_griffin_lim(self, mel_db, sr=22050, n_fft=2048, hop_length=256, win_length=2048, n_mels=80, fmax=8000):
        """Converts mel spectrogram back to audio using Griffin-Lim."""
        if self.mel_mean is None or self.mel_std is None:
            raise ValueError("Mel mean and standard deviation not loaded.")

        log_mel = (mel_db * self.mel_std) + self.mel_mean
        
        if log_mel.shape[1] == n_mels: # Already (time_steps, n_mels)
             mel_spec = librosa.db_to_power(log_mel.T)
        elif log_mel.shape[0] == n_mels: # Already (n_mels, time_steps)
             mel_spec = librosa.db_to_power(log_mel)
        else:
             raise ValueError(f"Unexpected mel_db shape: {mel_db.shape}. Expected (time_steps, n_mels) or (n_mels, time_steps).")

        mel_basis = librosa.filters.mel(sr=sr, n_fft=n_fft, n_mels=n_mels, fmax=fmax)
        inv_mel_basis = np.linalg.pinv(mel_basis)
        linear_spec = np.dot(inv_mel_basis, mel_spec)

        audio = librosa.griffinlim(linear_spec, hop_length=hop_length, win_length=win_length, n_iter=60)
        audio = audio / (np.max(np.abs(audio)) + 1e-6) # Normalize to prevent clipping
        return audio

    def synthesize(self, text: str) -> bytes:
        """
        Main function to synthesize speech from text.
        Returns audio data as bytes (WAV format).
        """
        if not self.is_loaded:
            raise RuntimeError("TTS models not loaded. Check server logs for errors.")

        print(f"TTS Inference: Processing text: '{text}'")

        normalized_text = self.normalizer.normalize_text(text)
        print(f"TTS Inference: Normalized text: '{normalized_text}'")

        phonemes = self.g2p.predict(normalized_text)
        print(f"TTS Inference: Phonemes: {phonemes}")

        # 3. Padding (use your actual maxlen)
        # You used maxlen=165 for your best_model in the test script.
        # Ensure consistency between training/testing/inference.
        # If your model expects two inputs (input_tensor, att_input),
        # adjust this padding accordingly.
        # Based on your test script, it seems `best_model.predict(input_tensor, verbose=0)[0]`
        # suggests only one input is passed now.
        
        max_seq_length = 165 # Or whatever your model expects
        padded_phonemes = pad_sequences([phonemes], maxlen=max_seq_length, padding='post')[0]
        input_tensor = tf.convert_to_tensor([padded_phonemes], dtype=tf.int32)

        # If your model *actually* requires two inputs (text_input, attention_input),
        # you would do something like this (uncomment if needed):
        # att_input = tf.zeros((1, tf.shape(input_tensor)[1]), dtype=tf.float32)
        # predicted_mel = self.best_model.predict((input_tensor, att_input), verbose=0)[0]
        
        # Current model prediction based on your test script:
        predicted_mel = self.best_model.predict(input_tensor, verbose=0)[0]
        print(f"TTS Inference: Predicted mel shape: {predicted_mel.shape} {predicted_mel}")

        # 4. Mel to Audio (Griffin-Lim)
        audio_data = self.mel_to_audio_griffin_lim(predicted_mel)
        print(f"TTS Inference: Generated audio data (length: {len(audio_data)} samples)")

        # Convert numpy array to bytes in WAV format
        # buffer = io.BytesIO()
        # sf.write(buffer, audio_data, 22050, format='WAV', subtype='PCM_16')
        sf.write("avatar_ui/static/audio/test.wav", audio_data, 22050)
        # buffer.seek(0)
        print(f"TTS Inference: predicted all over time: {datetime.datetime.now() - start} seconds")
        return audio_data

# Create a global instance of your TTS model.
# This ensures the models are loaded only once when the Flask app starts,
# not on every TTS request.

text="The second step we have taken in the restoration of normal business enterprise"
tts_model_instance = CustomTTS()
tts_model_instance.synthesize(text=text)

# You can add a check here if model loading failed during initialization
if not tts_model_instance.is_loaded:
    print("TTS: WARNING: CustomTTS model failed to load during initialization.")


# your_project_root/tts_pipeline/tts_inference.py

# import pyttsx3
# import io
# import os
# import time # For a small delay if needed

# class PyTTSx3Service:
#     def __init__(self):
#         self.engine = None
#         self.is_loaded = False
#         self._initialize_engine() # Initialize the engine on startup

#     def _initialize_engine(self):
#         """Initializes the pyttsx3 engine."""
#         try:
#             print("PyTTSx3Service: Initializing pyttsx3 engine...")
#             self.engine = pyttsx3.init()
            
#             # Set properties (optional, adjust as needed)
#             self.engine.setProperty('rate', 170)  # Speed of speech (words per minute)
#             self.engine.setProperty('volume', 1.0) # Volume (0.0 to 1.0)
            
#             # You can also change voices if available
#             # voices = self.engine.getProperty('voices')
#             # For example, to set a female voice (this is OS-dependent)
#             # self.engine.setProperty('voice', voices[1].id) 
            
#             print("PyTTSx3Service: pyttsx3 engine initialized successfully.")
#             self.is_loaded = True
#         except Exception as e:
#             print(f"PyTTSx3Service ERROR: Failed to initialize pyttsx3 engine: {e}")
#             self.is_loaded = False

#     def synthesize(self, text: str) -> bytes:
#         """
#         Synthesizes speech from text using pyttsx3 and returns it as WAV bytes.
#         """
#         if not self.is_loaded:
#             raise RuntimeError("PyTTSx3 engine not loaded. Cannot synthesize speech.")
#         if not text:
#             return b"" # Return empty bytes if no text

#         print(f"PyTTSx3Service: Synthesizing speech for: '{text}'")
        
#         # Create an in-memory byte buffer
#         audio_buffer = io.BytesIO()

#         # pyttsx3 can save to a file path. We'll save to a temporary file
#         # and then read it into the buffer. This is a common workaround as
#         # pyttsx3 doesn't directly support in-memory streams for saving.
#         temp_audio_file = "temp_pyttsx3_output.wav"
        
#         try:
#             self.engine.save_to_file(text, temp_audio_file)
#             self.engine.runAndWait() # This is crucial: waits for the audio to be generated and saved

#             # Wait a moment to ensure file is written, especially on slower systems
#             time.sleep(0.1) 

#             # Read the generated WAV file into the buffer
#             with open(temp_audio_file, "rb") as f:
#                 audio_buffer.write(f.read())
            
#             audio_buffer.seek(0) # Rewind the buffer to the beginning
#             print(f"PyTTSx3Service: Speech synthesis complete. Generated {len(audio_buffer.getvalue())} bytes.")
#             return audio_buffer.getvalue()
#         except Exception as e:
#             print(f"PyTTSx3Service ERROR: Error during synthesis: {e}")
#             raise # Re-raise the exception to be caught by Flask
#         finally:
#             # Clean up the temporary file
#             if os.path.exists(temp_audio_file):
#                 os.remove(temp_audio_file)

# # Create a global instance of the PyTTSx3Service.
# # This ensures the engine is initialized only once when your Flask app starts.
# tts_service_instance = PyTTSx3Service()

# # Optional: You can check if it loaded successfully
# if not tts_service_instance.is_loaded:
#     print("PyTTSx3Service: WARNING: PyTTSx3 engine failed to load during initialization.")

