import os
import logging
from dataclasses import dataclass
import sounddevice as sd
from scipy.io.wavfile import write
import subprocess
import threading
import queue
from pathlib import Path
import glob
from api_client import SpeechApiClient  # 새로운 import 추가

# 로깅 설정
from logging_config import setup_logging  # 새로운 import 추가

# 기존의 logging.getLogger().addHandler(handler) 부분을 제거하고
setup_logging()  # 이 줄로 대체
logger = logging.getLogger(__name__)


@dataclass
class Config:
    """설정값"""
    sample_rate: int = 16000
    channels: int = 1
    duration: int = 3
    model_path: str = "./whisper.cpp/models/ggml-base.bin"
    whisper_exec: str = "./whisper.cpp/build/bin/whisper-cli"
    language: str = "ko"

class VoiceProcessor:
    """음성 녹음 및 변환 처리"""
   
    def __init__(self):
        self.config = Config()
        self.queue = queue.Queue()
        self.is_running = True
        self.audio_index = 0
        self.api_client = SpeechApiClient()  # API 클라이언트 초기화
       
    def record(self):
        """녹음 처리"""
        while self.is_running:
            filename = f"audio_{self.audio_index}.wav"
            logger.info(f"녹음 중... ({filename})")
           
            # 녹음
            audio = sd.rec(
                int(self.config.duration * self.config.sample_rate),
                samplerate=self.config.sample_rate,
                channels=self.config.channels
            )
            sd.wait()
           
            # 저장
            write(filename, self.config.sample_rate, audio)
            logger.info(f"저장됨: {filename}")
            self.queue.put(filename)
            self.audio_index += 1
   
    def transcribe(self):
        """변환 처리"""
        while self.is_running:
            filename = self.queue.get()
            if filename is None:
                break
               
            logger.info(f"변환 중... ({filename})")
           
            # Whisper 변환
            result = subprocess.run(
                [
                    self.config.whisper_exec,
                    "-m", self.config.model_path,
                    "-f", filename,
                    "-l", self.config.language,
                    "-nt"
                ],
                capture_output=True,
                text=True,
            )
           
            # 결과 처리 및 API 전송
            if result.returncode == 0:
                transcribed_text = result.stdout.strip()
                logger.info(f"결과: {transcribed_text}")
                # API로 결과 전송
                self.api_client.send_transcription(transcribed_text)
            else:
                logger.error(f"변환 실패: {result.stderr}")

            # 큐 하나 비우기
            self.queue.task_done()
           
            # 임시 파일 삭제
            try:
                Path(filename).unlink()
            except:
                pass
   
    def start(self):
        """처리 시작"""
        # 변환 스레드 시작
        threading.Thread(target=self.transcribe, daemon=True).start()

        try:
            self.record()
        except KeyboardInterrupt:
            logger.info("🛑 중지됨")
        finally:
            self.stop()
   
    def stop(self):
        """처리 중지"""
        self.is_running = False
        self.queue.put(None)
    
    def exit(self):
        self.stop()
        self.is_running = False
        self.cleanup_audio_files()

    def cleanup_audio_files(self):
        """남아있는 임시 음성 파일 삭제"""
        for wav in glob.glob("audio_*.wav"):
            try:
                Path(wav).unlink()
                logger.info(f"임시 파일 삭제: {wav}")
            except Exception as e:
                logger.error(f"임시 파일 삭제 실패: {wav} ({e})")

if __name__ == "__main__":
    processor = VoiceProcessor()
    processor.start()
