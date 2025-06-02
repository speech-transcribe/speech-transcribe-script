import requests
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

class SpeechApiClient:
    """음성 인식 결과를 API 서버로 전송하는 클라이언트"""
    
    def __init__(self):
        # 환경변수에서 API 서버 IP 가져오기
        api_ip = os.getenv('API_SERVER_IP')
        if not api_ip:
            raise ValueError("API_SERVER_IP 환경변수가 설정되지 않았습니다.")
        
        self.api_url = f"http://{api_ip}:3000/speech-result"
        logger.info(f"API 서버 주소: {self.api_url}")
    
    def send_transcription(self, text: str) -> bool:
        """
        변환된 텍스트를 API 서버로 전송
        
        Args:
            text (str): 변환된 텍스트
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            data = {"text": text}
            response = requests.post(self.api_url, json=data)
            
            if response.status_code == 200:
                logger.info("API 전송 성공")
                return True
            else:
                logger.error(f"API 전송 실패: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API 연결 오류: {e}")
            return False 