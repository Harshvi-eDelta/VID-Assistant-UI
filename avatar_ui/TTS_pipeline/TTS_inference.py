import datetime
start = datetime.datetime.now()
import tensorflow as tf
import numpy as np
import librosa
import soundfile as sf
import io
import os
from avatar_ui.TTS_pipeline.text_preprocess import TextNormalizer
from avatar_ui.TTS_pipeline.hybrid_G2P import G2PConverter
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras import layers
from keras.saving import register_keras_serializable
from keras.config import enable_unsafe_deserialization
enable_unsafe_deserialization()

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
        query = tf.expand_dims(query, 1)

        f = self.location_conv(tf.expand_dims(prev_attention, -1))
        location_features = self.W_location(f)

        score = self.V(tf.nn.tanh(
            self.W_query(query) + self.W_values(values) + location_features))
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
        self._load_models()

    def _load_models(self):
        """Loads all necessary models and data."""
        try:
            custom_objects = {
                'CropLayer': CropLayer,
                'AdditiveAttention': AdditiveAttention,
                'AttentionContextLayer': AttentionContextLayer,
                'LocationSensitiveAttention': LocationSensitiveAttention,
                'LocationAttentionContextLayer': LocationAttentionContextLayer,
                'PositionalEncoding': PositionalEncoding,
                'LastTimestep': LastTimestep,
            }

            self.best_model = tf.keras.models.load_model(
                os.path.join(os.path.dirname(__file__), "models/2best_model_cnn_r_EarlyStopping.keras"),
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

    def mel_to_audio_griffin_lim(self, mel_db, sr=22050, n_fft=2048, hop_length=256, win_length=2048, n_mels=80, fmax=8000):
        """Converts mel spectrogram back to audio using Griffin-Lim."""
        if self.mel_mean is None or self.mel_std is None:
            raise ValueError("Mel mean and standard deviation not loaded.")

        log_mel = (mel_db * self.mel_std) + self.mel_mean
        
        if log_mel.shape[1] == n_mels:
             mel_spec = librosa.db_to_power(log_mel.T)
        elif log_mel.shape[0] == n_mels: 
             mel_spec = librosa.db_to_power(log_mel)
        else:
             raise ValueError(f"Unexpected mel_db shape: {mel_db.shape}. Expected (time_steps, n_mels) or (n_mels, time_steps).")

        mel_basis = librosa.filters.mel(sr=sr, n_fft=n_fft, n_mels=n_mels, fmax=fmax)
        inv_mel_basis = np.linalg.pinv(mel_basis)
        linear_spec = np.dot(inv_mel_basis, mel_spec)

        audio = librosa.griffinlim(linear_spec, hop_length=hop_length, win_length=win_length, n_iter=60)
        audio = audio / (np.max(np.abs(audio)) + 1e-6)
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
        
        max_seq_length = 165 
        padded_phonemes = pad_sequences([phonemes], maxlen=max_seq_length, padding='post')[0]
        input_tensor = tf.convert_to_tensor([padded_phonemes], dtype=tf.int32)
        
        predicted_mel = self.best_model.predict(input_tensor, verbose=0)[0]
        print(f"TTS Inference: Predicted mel shape: {predicted_mel.shape} {predicted_mel}")

        audio_data = self.mel_to_audio_griffin_lim(predicted_mel)
        print(f"TTS Inference: Generated audio data (length: {len(audio_data)} samples)")

        buffer = io.BytesIO()
        # print("====123",buffer)
        sf.write(buffer, audio_data, 22050, format='WAV', subtype='PCM_16')
        sf.write(f"avatar_ui/static/audio/{datetime.datetime.now()}.wav", audio_data, 22050)
        buffer.seek(0)
        print(f"TTS Inference: predicted all over time: {datetime.datetime.now() - start} seconds")
        return buffer.getvalue()

text="The second step we have taken in the restoration of normal business enterprise"
tts_model_instance = CustomTTS()
# tts_model_instance.synthesize(text=text)

if not tts_model_instance.is_loaded:
    print("TTS: WARNING: CustomTTS model failed to load during initialization.")

