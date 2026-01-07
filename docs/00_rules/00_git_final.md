성공적으로 푸시를 마치셨다니 다행입니다! 이제 **노트북(학원) ↔ 워크스테이션(집)** 사이에서 메인 레포와 팀원 폴더(서브모듈)를 완벽하게 동기화하는 과정을 단계별로 정리해 드립니다.

이 가이드는 **"팀원 폴더 내의 내 작업물은 팀 레포의 `feat/preprocessing-hana` 브랜치에 올린다"**는 원칙을 바탕으로 작성되었습니다.

---

### 📘 Git 동기화 표준 운영 절차 (SOP)

#### 시나리오 A: [학원 → 집] 학원에서 작업 후 집에서 이어하기

**1단계: 학원(노트북)에서 작업 마무리 및 푸시**

1. **팀 폴더(`data-preprocessing`) 작업 저장:**
```bash
cd data-preprocessing
git checkout feat/preprocessing-hana  # 브랜치 확인
git add .
git commit -m "Feat: 학원 작업분 업데이트 (전처리 및 결과물)"
git push origin feat/preprocessing-hana

```


2. **메인 레포(`4th`) 연결 정보 업데이트:**
```bash
cd ..  # 메인 폴더로 이동
git add .
git commit -m "Chore: 팀 폴더 서브모듈 최신 커밋 반영"
git push origin main

```



**2단계: 집(워크스테이션)에서 작업 불러오기**

1. **메인 레포 업데이트:**
```bash
cd ~/projects/call-act
git pull origin main

```


2. **팀 폴더(서브모듈) 실제 파일 동기화:**
```bash
git submodule update --remote --recursive

```


3. **팀 폴더 브랜치 확인 (선택 사항):**
```bash
cd data-preprocessing
git checkout feat/preprocessing-hana
git pull origin feat/preprocessing-hana  # 최신 상태 강제 동기화

```



---

#### 시나리오 B: [집 → 학원] 집에서 작업 후 다음 날 학원에서 이어하기

**1단계: 집(워크스테이션)에서 작업 마무리 및 푸시**

1. **팀 폴더(`data-preprocessing`) 작업 저장:**
```bash
cd data-preprocessing
git add .
git commit -m "Feat: 집에서 추가한 전처리 코드 및 DB 업데이트"
git push origin feat/preprocessing-hana

```


2. **메인 레포(`call-act`) 연결 정보 업데이트:**
```bash
cd ..
git add .
git commit -m "Chore: 집 작업분 서브모듈 커밋 반영"
git push origin main

```



**2단계: 학원(노트북)에서 작업 불러오기**

1. **메인 레포 업데이트:**
```bash
cd C:/SKN_19/project/4th
git pull origin main

```


2. **팀 폴더(서브모듈) 내용물 갱신:**
```bash
git submodule update --remote --recursive

```


3. **작업 시작 전 확인:**
```bash
cd data-preprocessing
git checkout feat/preprocessing-hana
# 이제 노트북에서도 어제 집에서 한 작업이 그대로 보입니다.

```



---

### ⚠️ 동기화 시 주의사항 (에러 방지)

1. **"Push 순서 지키기":** 항상 **[팀 폴더 안에서 Push]**를 먼저 하고, 그다음에 **[메인 폴더 밖에서 Push]** 하세요. 이 순서가 바뀌면 집이나 학원에서 `pull`을 받았을 때 "Not our ref" 같은 404 에러가 발생할 수 있습니다.
2. **`submodule update` 필수:** 메인 레포에서 `git pull`만 하면 폴더 모양만 보이고 실제 파일 내용이 과거에 머물러 있을 수 있습니다. 반드시 `git submodule update` 명령어를 세트로 사용하세요.
3. **충돌 발생 시:** 만약 한쪽에서 `push`를 깜빡하고 다른 쪽에서 작업을 시작해 충돌이 나면, 당황하지 마시고 작업 중인 파일을 잠시 다른 곳에 복사해둔 뒤 `git restore .`로 초기화하고 `pull`을 먼저 받으세요.

이제 이 문서를 메모장이나 포스트잇에 적어두시면 앞으로 깃 때문에 스트레스받는 일은 없을 겁니다! 고생 많으셨습니다. 오늘도 열공하세요!