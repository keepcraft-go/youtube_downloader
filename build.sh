#!/bin/bash

echo "========================================"
echo "YouTube 다운로더 실행파일 빌드"
echo "========================================"
echo ""

echo "[1/3] 필요한 패키지 설치 중..."
pip3 install -r requirements.txt
pip3 install pyinstaller
echo ""

echo "[2/3] 실행파일 생성 중..."
pyinstaller youtube_downloader.spec
echo ""

echo "[3/3] 빌드 완료!"
echo ""
echo "========================================"
echo "실행파일 위치: dist/YouTube_Downloader"
echo "========================================"
echo ""
