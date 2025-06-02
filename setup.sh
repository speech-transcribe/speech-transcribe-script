#!/bin/bash

set -e


# whisper.cpp 저장소 클론
if [[ ! -d "whisper.cpp" ]]; then
  git clone https://github.com/ggerganov/whisper.cpp.git
fi

cd whisper.cpp

# 최신 코드로 업데이트
git pull

# 빌드
# 실패하면 cmake 패키지가 있는지 확인하고 설치 후 재시도 필요
make

# 모델 디렉토리 생성
mkdir -p models

# tiny 모델 다운로드 (필요에 따라 다른 모델로 변경 가능)
if [ ! -f "models/ggml-base.bin" ]; then
  echo "모델 다운로드 중..."
  ./models/download-ggml-model.sh base
fi

echo "whisper.cpp 빌드, 모델 다운로드 완료"

cd ..

# 기존 venv 삭제 후 재생성 (심볼릭 링크 꼬임 방지)
if [ -d "venv" ]; then
  rm -rf venv
fi
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install sounddevice scipy requests

echo "python 가상환경 세팅 및 패키지 설치 완료!"
