import os
import logging
from dataclasses import dataclass
import sounddevice as sd
from scipy.io.wavfile import write
import subprocess
import threading
import queue
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Config:
    """설정값"""
    sample_rate: int = 16000
    channels: int = 1
    duration: int = 3
    model_path: str = "./whisper.cpp/models/ggml-tiny.bin"
    whisper_exec: str = "./whisper.cpp/build/bin/whisper-cli"
    language: str = "ko"

class VoiceProcessor:
    """음성 녹음 및 변환 처리"""
   
    def __init__(self):
        self.config = Config()
        self.queue = queue.Queue()
        self.is_running = True
        self.audio_index = 0
       
    def record(self):
        """녹음 처리"""
        while self.is_running:
            filename = f"audio_{self.audio_index}.wav"
            logger.info(f" 녹음 중... ({filename})")
           
            # 녹음
            audio = sd.rec(
                int(self.config.duration * self.config.sample_rate),
                samplerate=self.config.sample_rate,
                channels=self.config.channels
            )
            sd.wait()
           
            # 저장
            write(filename, self.config.sample_rate, audio)
            logger.info(f"✅ 저장됨: {filename}")
            self.queue.put(filename)
            self.audio_index += 1
   
    def transcribe(self):
        """변환 처리"""
        while self.is_running:
            filename = self.queue.get()
            if filename is None:
                break
               
            logger.info(f"🧠 변환 중... ({filename})")
           
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
                shell=True
            )
           
            # 결과 출력
            if result.returncode == 0:
                logger.info(f"🗣 결과: {result.stdout.strip()}")
            else:
                logger.error(f"변환 실패: {result.stderr}")
           
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
            # 녹음 시작
            self.record()
        except KeyboardInterrupt:
            logger.info("🛑 중지됨")
        finally:
            self.stop()
   
    def stop(self):
        """처리 중지"""
        self.is_running = False
        self.queue.put(None)

if __name__ == "__main__":
    processor = VoiceProcessor()
    processor.start()