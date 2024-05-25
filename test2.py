import requests
import numpy as np
from scipy.io.wavfile import write
import wave

STREAM_URL = "http://localhost:8010/tts/tts_stream_chunk?text=hi%20my%20name%20is%20posilping"

def receive_and_save_audio(url, output_file):
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()  # 요청 실패 시 예외 발생
            # 최종 오디오 데이터를 저장할 리스트
            audio_data = []
            for chunk in r.iter_content(chunk_size=None):  # 서버에서 정의된 스트림 방식을 따름
                if chunk:
                    print("chunk: ",chunk)
                    # 받은 데이터를 numpy array로 변환
                    audio_chunk = np.frombuffer(chunk, dtype=np.float32)
                    print("float: ",audio_chunk)
                    audio_data.append(audio_chunk)
                
            audio_data = np.concatenate(audio_data)
            print("combined_audio:",audio_data)
            with wave.open(output_file, 'wb') as wf:
            # WAV 파일의 설정 (예: 채널 수, 샘플 폭, 샘플링 레이트 등)
                n_channels = 1  # 모노
                sampwidth = 2  # 16비트 오디오
                framerate = 24000  # 표준 샘플링 레이트
                n_frames = len(audio_data)

                # WAV 파일의 파라미터 설정
                wf.setnchannels(n_channels)
                wf.setsampwidth(sampwidth)
                wf.setframerate(framerate)
                wf.setnframes(n_frames)
                wf.writeframes(audio_data.tobytes())
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    receive_and_save_audio(STREAM_URL, "output_audio.wav")
