from concurrent.futures import ThreadPoolExecutor
import os
import torch
from flask import current_app as app
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from TTS.utils.manage import ModelManager
from TTS.utils.generic_utils import get_user_data_dir
import threading
import langid
import re
import time
import torchaudio
import io
import noisereduce as nr
import numpy as np
import wave
import base64

def postprocess(wav):
    """Post process the output waveform"""
    if isinstance(wav, list):
        wav = torch.cat(wav, dim=0)
    wav = wav.clone().detach().cpu().numpy()
    wav = wav[None, : int(wav.shape[0])]
    wav = np.clip(wav, -1, 1)
    wav = (wav * 32767).astype(np.int16)
    return wav

def encode_audio_common(
    frame_input, encode_base64=True, sample_rate=24000, sample_width=2, channels=1
):
    """Return base64 encoded audio"""
    wav_buf = io.BytesIO()
    with wave.open(wav_buf, "wb") as vfout:
        vfout.setnchannels(channels)
        vfout.setsampwidth(sample_width)
        vfout.setframerate(sample_rate)
        vfout.writeframes(frame_input)

    wav_buf.seek(0)
    if encode_base64:
        b64_encoded = base64.b64encode(wav_buf.getbuffer()).decode("utf-8")
        return b64_encoded
    else:
        return wav_buf.read()

class AppContext:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'model_initialized'):
            self.model = None
            self.config = {}
            self.model_initialized = False

    def initialize_model(self):
        if not self.model_initialized:
            model_path = "./XTTS-v2"
            config = XttsConfig()
            config.load_json(os.path.join(model_path, "config.json"))
            self.model = Xtts.init_from_config(config)
            self.model.load_checkpoint(
                config,
                speaker_file_path=os.path.join(model_path, "speakers_xtts.pth"),
                checkpoint_path=os.path.join(model_path, "model.pth"),
                vocab_path=os.path.join(model_path, "vocab.json"),
                eval=True,
                # use_deepspeed=True
            )
            self.model.to('cpu')
            self.model.eval()
            self.config = config
            self.model_initialized = True
            print("model is initialized")

    def predict_tts(self, id, text, language, audio_file_pth):
        return predict(id, text, language, audio_file_pth)

    def streaming_tts(self, text, language, audio_file_pth):
        print("Loading model...")
        model = self.model
        try:
            (gpt_cond_latent,
                speaker_embedding,
                ) = model.get_conditioning_latents(audio_path=audio_file_pth)
        except Exception as e:
            print(f"Error during conditioning latent extraction: {str(e)}")
            return f"Error: {str(e)}"  # Flask에서는 단순 텍스트를 반환
        
        def generator():
            print("Inference...")
            t0 = time.time()
            wav_chuncks = []
            chunks = model.inference_stream(
                text,
                language,
                gpt_cond_latent,
                speaker_embedding
            )
            for i, chunk in enumerate(chunks):
                now = time.time()
                if i == 0:
                    print(f"Time to first chunk: {now - t0} seconds")
                print(f"Received chunk {i} of audio length {chunk.shape[-1]}")
                wav_chuncks.append(chunk)
                data = torch.tensor(chunk).squeeze().unsqueeze(0).cpu().numpy().tobytes()
                yield data
                print(f"Total inference time so far: {time.time() - t0} seconds")
            wav = torch.cat(wav_chuncks, dim=0)
            torchaudio.save("streaming.wav", wav.squeeze().unsqueeze(0).cpu(), 24000)

        return generator()

    def tts_stream_with_chunk(self, text, chunk_size, language, audio_file_pth):
        model = self.model
        # chunk_size = int(
        #     model.get("chunk_size", 150)
        # )
        # print("chunk_size: ",chunk_size)
        try:
            (gpt_cond_latent,
            speaker_embedding,
            ) = model.get_conditioning_latents(audio_path=audio_file_pth)
        except Exception as e:
            print(f"Error during conditioning latent extraction: {str(e)}")
            return f"Error: {str(e)}"
        
        print("Inference...")
        def generator():
            chunks = model.inference_stream(
                text,
                language,
                gpt_cond_latent,
                speaker_embedding,
                stream_chunk_size=chunk_size,
                overlap_wav_len=1024,
                enable_text_splitting=True,
            )
            # for chunk in chunks:
            #     print(f"Received chunk n of audio length {chunk.shape[-1]}")
            #     data = chunk.squeeze().cpu().numpy().tobytes()
            #     # data = np.frombuffer(data, dtype=np.float32)
            #     yield data
            for i, chunk in enumerate(chunks):
                chunk = postprocess(chunk)
                if i == 0:
                    yield encode_audio_common(b"", encode_base64=False)
                    yield chunk.tobytes()
                else:
                    yield chunk.tobytes()
        return generator
    
    def tts_stream_with_chunk_static(self, text, language, audio_file_pth):
        model = self.model
        # chunk_size = int(
        #     model.get("chunk_size", 150)
        # )
        # print("chunk_size: ",chunk_size)
        try:
            (gpt_cond_latent,
            speaker_embedding,
            ) = model.get_conditioning_latents(audio_path=audio_file_pth)
        except Exception as e:
            print(f"Error during conditioning latent extraction: {str(e)}")
            return f"Error: {str(e)}"
        
        print("Inference...")
        def generator():
            chunks = model.inference_stream(
                text,
                language,
                gpt_cond_latent,
                speaker_embedding,
                stream_chunk_size=20,
                overlap_wav_len=1024,
                enable_text_splitting=True,
            )
            # for chunk in chunks:
            #     print(f"Received chunk n of audio length {chunk.shape[-1]}")
            #     data = chunk.squeeze().cpu().numpy().tobytes()
            #     # data = np.frombuffer(data, dtype=np.float32)
            #     yield data
            for i, chunk in enumerate(chunks):
                chunk = postprocess(chunk)
                if i == 0:
                    yield encode_audio_common(b"", encode_base64=False)
                    yield chunk.tobytes()
                else:
                    yield chunk.tobytes()
        return generator
        

def predict(id, text, language, audio_file_pth):
    model = AppContext.get_instance().model
    speaker_wav = audio_file_pth

    if len(text) < 2:
        return None
    if len(text) > 200:
        return None

    try:
        metrics_text = ""
        t_latent = time.time()
        
        try:
            (gpt_cond_latent,
            speaker_embedding,
            ) = model.get_conditioning_latents(audio_path=speaker_wav)
            #model.get_conditioning_latents(audio_path=speaker_wav, gpt_cond_len=30, gpt_cond_chunk_len=4, max_ref_length=60)
        except Exception as e:
            print("Speaker encoding error", str(e))
            return e
        latent_calculation_time = time.time() - t_latent
        print("latent_calculation_time",latent_calculation_time)
        text= re.sub("([^\x00-\x7F]|\w)(\.|\。|\?)",r"\1 \2\2",text)
        print("I: Generating new audio...")
        t0 = time.time()
        out = model.inference(
            text,
            language,
            gpt_cond_latent,
            speaker_embedding,
            repetition_penalty=5.0,
            temperature=0.75,
        )
        inference_time = time.time() - t0
        print(f"I: Time to generate audio: {round(inference_time*1000)} milliseconds")
        metrics_text+=f"Time to generate audio: {round(inference_time*1000)} milliseconds\n"
        real_time_factor= (time.time() - t0) / out['wav'].shape[-1] * 24000
        print(f"Real-time factor (RTF): {real_time_factor}")
        metrics_text+=f"Real-time factor (RTF): {real_time_factor:.2f}\n"
        try :
            buffer = io.BytesIO()
            torchaudio.save(buffer, torch.tensor(out["wav"]).unsqueeze(0), 24000, format="wav")
            buffer.seek(0)
            return buffer
        except Exception as e:
            print(f"Error during saving audio: {e}")
            return e

    except Exception as e:
        print(f"Error during conditioning latent extraction: {e}")
        return e