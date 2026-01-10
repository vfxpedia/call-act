# 임베딩 생성 백그라운드 실행 가이드

## ⚠️ 중요: CMD에서 conda 오류 발생 시

**오류 메시지**:
```
'conda'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.
```

**해결 방법**: **Anaconda Prompt 사용** (가장 간단) ⭐

**Windows 시작 메뉴**:
1. 시작 메뉴에서 "Anaconda Prompt" 검색
2. "Anaconda Prompt" 실행

**Anaconda Prompt에서 실행**:
```bash
cd C:\Users\AI-WS01\projects\call-act
conda activate final_env
cd scripts\db_loading
python generate_embeddings_hana.py
```

**상세 가이드**: `docs/04_dev/02_db/07_CMD_conda_오류_해결.md` 참조

---

## Windows에서 백그라운드 실행 방법

### 방법 1: Anaconda Prompt에서 실행 (가장 간단) ⭐ 추천

**Anaconda Prompt** (Windows 시작 메뉴에서 실행):

```bash
# Anaconda Prompt에서 실행
cd C:\Users\AI-WS01\projects\call-act
conda activate final_env
cd scripts\db_loading

# 실행 (로그는 embedding_generation.log에 자동 저장)
python generate_embeddings_hana.py

# 창은 그대로 두고 (최소화 가능) 다른 작업 가능
```

**장점**: 
- ✅ conda 명령어 자동 인식
- ✅ 별도 설정 불필요
- ✅ 가장 안정적

### 방법 2: 배치 파일 실행 (Anaconda Prompt에서)

```bash
# Anaconda Prompt에서 실행
cd C:\Users\AI-WS01\projects\call-act\scripts\db_loading
.\run_embeddings_background.bat

# 창을 최소화하고 다른 작업 가능
# 로그는 embedding_generation.log 파일에 자동 저장
```

### 방법 2: PowerShell 백그라운드 실행

```powershell
# 새 PowerShell 창에서 실행 (현재 창 닫아도 됨)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\AI-WS01\projects\call-act\scripts\db_loading; conda activate final_env; python generate_embeddings_hana.py"

# 별도 PowerShell 창에서 로그 확인
Get-Content scripts\db_loading\embedding_generation.log -Wait -Tail 50
```

### 방법 3: 리다이렉트로 실행

```powershell
conda activate final_env
cd scripts/db_loading

# 출력을 파일로 리다이렉트
python generate_embeddings_hana.py > embedding_console.log 2>&1

# 별도 창에서 진행 상황 확인
Get-Content embedding_generation.log -Wait -Tail 50
```

## 로그 확인

### 실시간 로그 확인
```powershell
# PowerShell
Get-Content scripts\db_loading\embedding_generation.log -Wait -Tail 50

# 또는 cmd
type scripts\db_loading\embedding_generation.log
```

### 최종 요약 확인
```powershell
# SUMMARY 섹션만 확인
Get-Content scripts\db_loading\embedding_generation.log | Select-String "SUMMARY" -Context 0,10
```

## 진행 상황 확인

### 체크포인트 확인
```powershell
# 처리된 문서 수 확인
Get-Content scripts\db_loading\embedding_checkpoint.json | ConvertFrom-Json
```

### 출력 파일 확인
```powershell
# 파일 크기 확인
Get-Item data-preprocessing\data\hana\hana_vectordb_with_embeddings.json | Select-Object Length, LastWriteTime
```

## 재시작 (중단된 경우)

```powershell
conda activate final_env
cd scripts/db_loading
python generate_embeddings_hana.py --resume
```

## 주의사항

- ✅ 컴퓨터를 끄면 안 됨
- ✅ 네트워크 연결 유지 (OpenAI API 호출)
- ✅ 전원 설정 확인 (절전 모드 비활성화 권장)
- ✅ 체크포인트 자동 저장 (100개마다)

