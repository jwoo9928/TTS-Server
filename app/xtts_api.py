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
                eval=True
            )
            self.model.eval()
            self.config = config
            self.model_initialized = True
            print("model is initialized")
    def predict_tts(self, text, language, audio_file_pth):
        return predict(text, language, audio_file_pth)

def predict(text, language, audio_file_pth):
    model = AppContext.get_instance().model
    config = AppContext.get_instance().config

    language_predicted = langid.classify(text)[0].strip()
    speaker_wav = audio_file_pth
    lowpassfilter = denoise = trim = loudness = True

    if lowpassfilter:
        lowpass_highpass = "lowpass=8000,highpass=75,"
    else:
        lowpass_highpass = ""

    if trim:
            # better to remove silence in beginning and end for microphone
        trim_silence = "areverse,silenceremove=start_periods=1:start_silence=0:start_threshold=0.02,areverse,silenceremove=start_periods=1:start_silence=0:start_threshold=0.02,"
    else:
        trim_silence = ""

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
            ) = model.get_conditioning_latents(audio_path=speaker_wav, gpt_cond_len=30, gpt_cond_chunk_len=4, max_ref_length=60)
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
        torchaudio.save("output.wav", torch.tensor(out["wav"]).unsqueeze(0), 24000)

    except Exception as e:
        print(f"Error during conditioning latent extraction: {e}")
        return e