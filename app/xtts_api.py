from concurrent.futures import ThreadPoolExecutor
import os
import torch
from flask import current_app as app
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from TTS.utils.manage import ModelManager
from TTS.utils.generic_utils import get_user_data_dir
from TTS.utils.io import load_config
import langid
import re
import time

executor = ThreadPoolExecutor(max_workers=4)


# 모델 및 설정 초기화 및 로딩을 위한 함수
def initialize_model():
    model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
    # 모델 다운로드 경로
    model_path = os.path.join(get_user_data_dir("tts"), model_name.replace("/", "--"))
    
    # 모델 설정 로드
    config = XttsConfig()
    
    # 모델 인스턴스화 및 체크포인트 로드
    model = Xtts(config)
    model.load_state_dict(torch.load(os.path.join(model_path, "model.pth"), map_location=torch.device('cpu')))
    model.eval()
    
    app.config['xtts_model'] = model
    app.config['xtts_config'] = config

# 텍스트를 음성으로 변환하는 함수
def text_to_speech(text, language="en"):
    model = app.config['xtts_model']
    config = app.config['xtts_config']
    
    # 텍스트를 음성으로 변환
    try:
        # 입력 텍스트를 모델이 처리할 수 있는 형태로 준비
        # inputs = model.prepare_input_sequence([text])
        inputs = {
            "text": text,
            "language": language,
            "gpt_cond_latent": None,  # 고정 옵션
            "speaker_embedding": None,  # 고정 옵션
            "repetition_penalty": 1.0,  # 고정 옵션
            "temperature": 1.0,  # 고정 옵션
        }
        
        # 음성 생성
        with torch.no_grad():
            # outputs = model.inference(**inputs)
            outputs = model.inference(
                text=inputs['text'],
                language=inputs['language'],
                gpt_cond_latent=inputs['gpt_cond_latent'],
                speaker_embedding=inputs['speaker_embedding'],
                repetition_penalty=inputs['repetition_penalty'],
                temperature=inputs['temperature']
            )
        
        # 생성된 오디오 데이터를 wav 파일로 저장
        output_path = f"{text[:10]}_{language}.wav"  # 파일 이름 예제
        model.save_wav(outputs['wav'], output_path)
        
        return output_path
    except Exception as e:
        print(f"Error during text-to-speech conversion: {e}")
        return None

def predict(text, language, audio_file_pth):
    model = app.config['xtts_model']
    config = app.config['xtts_config']

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


def gen_tts(text, language="en"):
    future = executor.submit(text_to_speech, text, language)
    return future.result()

def predict_tts(text, language, audio_file_path):
    future = executor.submit(predict, text, language, audio_file_path)
    return future.result()