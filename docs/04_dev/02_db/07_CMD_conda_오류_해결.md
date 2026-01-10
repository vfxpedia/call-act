# CMD에서 conda 명령어 오류 해결 가이드

**작성일**: 2026-01-09  
**작성자**: CALL:ACT Team  
**버전**: v1.0

---

## ❌ 오류 메시지

```
'conda'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.
```

---

## 🔍 원인

Windows CMD(일반 명령 프롬프트)에서는 conda 명령어가 기본적으로 PATH에 등록되지 않아 인식되지 않습니다.

---

## ✅ 해결 방법

### 방법 1: Anaconda Prompt 사용 (가장 간단) ⭐ **권장**

**Windows 시작 메뉴**:
1. 시작 메뉴 열기
2. "Anaconda Prompt" 검색
3. "Anaconda Prompt" 실행 (또는 "Anaconda PowerShell Prompt")

**Anaconda Prompt에서 실행**:
```bash
# 1. 프로젝트 폴더로 이동
cd C:\Users\AI-WS01\projects\call-act

# 2. Conda 환경 활성화
conda activate final_env

# 3. 작업 폴더로 이동
cd scripts\db_loading

# 4. 임베딩 생성 실행
python generate_embeddings_hana.py

# 5. 창은 그대로 두고 (최소화 가능) 다른 작업 가능
# 로그는 embedding_generation.log 파일에 자동 저장
```

**장점**:
- ✅ 별도 설정 불필요
- ✅ conda 명령어 자동 인식
- ✅ 가장 안정적
- ✅ 즉시 사용 가능

---

### 방법 2: CMD에서 conda 초기화

**1단계: Anaconda 설치 경로 확인**

일반적인 설치 경로:
- `C:\Users\[사용자명]\anaconda3`
- `C:\ProgramData\anaconda3`

**확인 방법**:
```bash
# PowerShell에서
where.exe conda

# 또는
Get-Command conda -ErrorAction SilentlyContinue
```

**2단계: conda 초기화 (CMD용)**

```bash
# Anaconda 설치 경로 확인 후 실행
# 예시: C:\Users\AI-WS01\anaconda3\Scripts\conda.exe init cmd.exe

# Anaconda Prompt에서 실행하거나
# 또는 직접 경로 지정:
C:\Users\AI-WS01\anaconda3\Scripts\conda.exe init cmd.exe
```

**3단계: CMD 재시작**

- 현재 CMD 창 닫기
- 새 CMD 창 열기

**4단계: 확인**

```bash
conda --version
# 출력: conda 23.x.x 또는 conda 24.x.x

conda env list
# 가상환경 목록 확인
```

---

### 방법 3: PATH 환경 변수에 conda 추가

**1단계: 시스템 환경 변수 설정**

1. Windows 검색 → "환경 변수" → "시스템 환경 변수 편집" 선택
2. "환경 변수" 버튼 클릭
3. "시스템 변수" 섹션에서 "Path" 선택
4. "편집" 클릭
5. "새로 만들기" 클릭하여 다음 경로 추가:

```
C:\Users\AI-WS01\anaconda3
C:\Users\AI-WS01\anaconda3\Scripts
C:\Users\AI-WS01\anaconda3\Library\bin
```

**참고**: 경로는 실제 Anaconda 설치 경로로 변경하세요.

**2단계: 확인**

- 모든 창 닫기
- 새 CMD 창 열기

```bash
conda --version
# 출력: conda 23.x.x 또는 conda 24.x.x
```

---

### 방법 4: Anaconda 설치 확인 및 재설치

**Anaconda가 설치되어 있는지 확인**:

**PowerShell에서**:
```powershell
# conda 명령어 찾기
Get-Command conda -ErrorAction SilentlyContinue

# 또는
where.exe conda
```

**설치되어 있지 않은 경우**:

1. **Anaconda 다운로드**:
   - https://www.anaconda.com/download 에서 다운로드
   - Windows 64-bit 버전 선택

2. **Anaconda 설치**:
   - 설치 프로그램 실행
   - **중요**: "Add Anaconda to PATH" 옵션 체크 (권장)
   - 기본 경로로 설치 (일반적으로 `C:\Users\[사용자명]\anaconda3`)

3. **재시작**:
   - 컴퓨터 재시작 (또는 새 CMD 창 열기)

4. **확인**:
   ```bash
   conda --version
   # 출력: conda 23.x.x 또는 conda 24.x.x
   ```

---

## 🚀 빠른 해결 (지금 바로 실행)

### 가장 간단한 방법

**Anaconda Prompt 사용**:

1. **Windows 시작 메뉴** → "Anaconda Prompt" 검색 → 실행

2. **명령어 실행**:
   ```bash
   cd C:\Users\AI-WS01\projects\call-act
   conda activate final_env
   cd scripts\db_loading
   python generate_embeddings_hana.py
   ```

3. **완료!** 
   - conda 명령어 정상 작동
   - 임베딩 생성 시작
   - 로그는 `embedding_generation.log`에 자동 저장

---

## 📝 참고사항

### Anaconda vs Miniconda

- **Anaconda**: 전체 패키지 포함 (용량 큼, 약 3GB)
- **Miniconda**: 최소 설치 (용량 작음, 약 400MB)
- **둘 다 conda 명령어 사용**: 차이 없음

### conda 명령어가 작동하는 환경

- ✅ **Anaconda Prompt** (자동 설정)
- ✅ **Anaconda PowerShell Prompt** (자동 설정)
- ❌ **일반 CMD** (수동 설정 필요)
- ❌ **일반 PowerShell** (수동 설정 필요)

### 권장 사항

**개발 작업**: Anaconda Prompt 사용 ⭐
- 별도 설정 불필요
- 즉시 사용 가능
- 안정적

**배치 작업**: conda 초기화 또는 PATH 설정
- 자동화 스크립트에서 사용
- 설정 필요

---

## ✅ 확인 방법

### 1. conda 설치 확인

**Anaconda Prompt에서**:
```bash
conda --version
# 출력: conda 23.x.x 또는 conda 24.x.x
```

**일반 CMD에서** (초기화 또는 PATH 설정 후):
```bash
conda --version
# 출력: conda 23.x.x 또는 conda 24.x.x
```

### 2. 가상환경 확인

```bash
# 가상환경 목록 확인
conda env list

# 출력 예시:
# base                     C:\Users\AI-WS01\anaconda3
# final_env             *  C:\Users\AI-WS01\anaconda3\envs\final_env
# 
# * 표시가 있는 것이 현재 활성화된 환경
```

### 3. Python 버전 확인

```bash
conda activate final_env
python --version
# 출력: Python 3.11.x
```

---

## 🎯 다음 단계

conda 명령어가 정상 작동하면:

1. **가상환경 생성** (아직 생성하지 않았다면):
   ```bash
   conda env create -f scripts/environment.yml
   ```

2. **가상환경 활성화**:
   ```bash
   conda activate final_env
   ```

3. **패키지 설치**:
   ```bash
   pip install -r scripts/requirements.txt
   ```

4. **임베딩 생성**:
   ```bash
   cd scripts/db_loading
   python generate_embeddings_hana.py
   ```

---

## 🔗 참고 문서

- 개발 환경 설정: `docs/04_dev/02_db/01_개발환경_설정_가이드.md`
- 실행 가이드: `docs/04_dev/02_db/02_실행_가이드.md`
- 작업 순서: `docs/04_dev/02_db/06_작업_순서_및_백그라운드_실행.md`

