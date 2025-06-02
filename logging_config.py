import logging

def setup_logging():
    if not logging.getLogger().handlers:  # 핸들러가 없을 때만 설정
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(message)s',
            datefmt='%H:%M:%S'
        )