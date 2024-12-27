import requests
import numpy as np
from scipy.io.wavfile import write

STREAM_URL = "http://localhost:8010/tts/tts_stream_chunk?text=hi%20my%20name%20is%20posilping"

def receive_and_save_audio(url, output_file):
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()  # 요청 실패 시 예외 발생
            # 최종 오디오 데이터를 저장할 리스트
            audio_data = []
            for chunk in r.iter_content(chunk_size=240):  # 서버에서 정의된 스트림 방식을 따름
                if chunk:
                    # 받은 데이터를 numpy array로 변환
                    audio_chunk = np.frombuffer(chunk, dtype=np.float32)
                    audio_data.append(audio_chunk)
                
            combined_audio = np.concatenate(audio_data)
            print("combined_audio:",combined_audio)
            write(output_file, 24000, combined_audio)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    receive_and_save_audio(STREAM_URL, "output_audio.wav")
