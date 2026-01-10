@echo off
REM 하나카드 임베딩 생성 백그라운드 실행 배치 파일
REM 사용법: Anaconda Prompt에서 실행하거나, Anaconda 설치 경로를 수정하세요

echo ========================================
echo Embedding Generation Started
echo ========================================
echo.
echo [INFO] This script should be run from Anaconda Prompt
echo [INFO] Or modify the conda path below
echo.

cd /d %~dp0
cd ..

REM Anaconda 설치 경로 확인 (사용자에 따라 수정 필요)
REM 일반적인 경로:
REM C:\Users\%USERNAME%\anaconda3
REM C:\ProgramData\anaconda3

REM 방법 1: Anaconda Prompt에서 실행 시 (권장)
REM 아래 주석 해제하고 Anaconda Prompt에서 실행

REM Conda 환경 활성화
call conda activate final_env
if errorlevel 1 (
    echo [ERROR] Failed to activate conda environment
    echo [INFO] Please run this script from Anaconda Prompt
    echo [INFO] Or check if conda is installed and in PATH
    pause
    exit /b 1
)

REM 임베딩 생성 실행
cd scripts\db_loading
echo Current directory: %CD%
echo.
echo Starting embedding generation...
echo Log file: embedding_generation.log
echo.

python generate_embeddings_hana.py

echo.
echo ========================================
echo Embedding Generation Completed
echo ========================================
echo.
echo Log file: scripts\db_loading\embedding_generation.log
echo Output file: data-preprocessing\data\hana\hana_vectordb_with_embeddings.json
echo.
pause

