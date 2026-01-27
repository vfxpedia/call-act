# 25. Git 워크플로우

> **CALL:ACT 프로젝트의 브랜치 전략 및 커밋 규칙**

## 목차
- [1. 브랜치 전략](#1-브랜치-전략)
- [2. 커밋 메시지 규칙](#2-커밋-메시지-규칙)
- [3. PR 프로세스](#3-pr-프로세스)
- [4. 코드 리뷰 가이드](#4-코드-리뷰-가이드)
- [5. Git 명령어 가이드](#5-git-명령어-가이드)

---

## 1. 브랜치 전략

### 1.1 브랜치 구조 (Git Flow 기반)

```
main (프로덕션)
  ↑
develop (개발)
  ↑
  ├─ feature/login-page
  ├─ feature/dashboard
  ├─ feature/consultation-live
  ├─ bugfix/sidebar-overlap
  ├─ hotfix/critical-security
  └─ docs/api-specification
```

### 1.2 브랜치 종류

#### 1.2.1 Main 브랜치

**목적**: 프로덕션 배포용 (항상 안정적)

```bash
# main 브랜치는 직접 커밋 금지
# develop에서 PR을 통해서만 병합
```

**규칙**:
- ✅ develop에서 PR 병합만 허용
- ✅ 태그를 통한 버전 관리 (`v1.0.0`, `v1.1.0`)
- ❌ 직접 커밋 금지
- ❌ Force Push 금지

#### 1.2.2 Develop 브랜치

**목적**: 개발 통합 브랜치

```bash
# develop 브랜치에서 feature 브랜치 생성
git checkout develop
git pull origin develop
git checkout -b feature/new-feature
```

**규칙**:
- ✅ feature 브랜치의 병합 대상
- ✅ 기능 개발 완료 후 main으로 PR
- ❌ 불안정한 코드 병합 금지

#### 1.2.3 Feature 브랜치

**목적**: 새로운 기능 개발

**명명 규칙**: `feature/기능명-간략설명`

```bash
✅ 올바른 예시:
feature/login-page
feature/dashboard-stats
feature/consultation-live
feature/kanban-board
feature/stt-integration

❌ 잘못된 예시:
feature/new
feature/update
feature/fix
login-page
```

**생성 및 작업**:
```bash
# 1. develop에서 최신 코드 pull
git checkout develop
git pull origin develop

# 2. feature 브랜치 생성
git checkout -b feature/login-page

# 3. 작업 후 커밋
git add .
git commit -m "feat: 로그인 페이지 UI 구현"

# 4. 원격 브랜치에 push
git push origin feature/login-page

# 5. GitHub에서 PR 생성 (feature/login-page → develop)
```

#### 1.2.4 Bugfix 브랜치

**목적**: 버그 수정

**명명 규칙**: `bugfix/버그명-간략설명`

```bash
✅ 올바른 예시:
bugfix/sidebar-overlap
bugfix/pagination-error
bugfix/modal-close-issue

❌ 잘못된 예시:
bugfix/fix
bugfix/error
fix/sidebar
```

#### 1.2.5 Hotfix 브랜치

**목적**: 프로덕션 긴급 수정

**명명 규칙**: `hotfix/버전-이슈명`

```bash
✅ 올바른 예시:
hotfix/v1.0.1-security-patch
hotfix/v1.0.2-critical-bug

# main에서 직접 분기
git checkout main
git checkout -b hotfix/v1.0.1-security-patch

# 수정 후 main과 develop 둘 다 병합
git checkout main
git merge hotfix/v1.0.1-security-patch
git tag v1.0.1

git checkout develop
git merge hotfix/v1.0.1-security-patch
```

#### 1.2.6 Docs 브랜치

**목적**: 문서 작업

**명명 규칙**: `docs/문서명`

```bash
✅ 올바른 예시:
docs/api-specification
docs/coding-convention
docs/deployment-guide
```

---

## 2. 커밋 메시지 규칙

### 2.1 Conventional Commits 형식

**기본 형식**:
```
<타입>(<스코프>): <제목>

<본문>

<푸터>
```

### 2.2 커밋 타입

| 타입 | 설명 | 예시 |
|------|------|------|
| **feat** | 새로운 기능 추가 | `feat: 로그인 페이지 구현` |
| **fix** | 버그 수정 | `fix: 사이드바 오버랩 이슈 해결` |
| **docs** | 문서 수정 | `docs: API 명세서 업데이트` |
| **style** | 코드 포맷팅 (기능 변경 없음) | `style: Tailwind 클래스 순서 정리` |
| **refactor** | 코드 리팩토링 | `refactor: 칸반보드 컴포넌트 분리` |
| **perf** | 성능 개선 | `perf: 이미지 로딩 최적화` |
| **test** | 테스트 추가/수정 | `test: 로그인 유닛 테스트 추가` |
| **chore** | 빌드/설정 변경 | `chore: Vite 설정 업데이트` |
| **revert** | 커밋 되돌리기 | `revert: feat: 로그인 페이지 구현` |

### 2.3 커밋 메시지 예시

#### 2.3.1 제목만 있는 경우 (간단한 변경)

```bash
✅ 올바른 예시:
git commit -m "feat: 로그인 페이지 UI 구현"
git commit -m "fix: 페이지네이션 버그 수정"
git commit -m "docs: README 업데이트"
git commit -m "style: 코드 포맷팅 정리"
git commit -m "refactor: 사원 관리 모달 컴포넌트 분리"

❌ 잘못된 예시:
git commit -m "로그인 페이지"
git commit -m "수정"
git commit -m "update"
git commit -m "fix bug"
git commit -m "add feature"
```

#### 2.3.2 본문이 있는 경우 (복잡한 변경)

```bash
git commit -m "feat: 실시간 상담 페이지 STT 통합

- STT 시뮬레이션 기능 구현
- 키워드 자동 추출 로직 추가
- 대화 내용 실시간 표시
- 칸반보드와 STT 연동

관련 이슈: #123"
```

#### 2.3.3 Breaking Change (호환성 깨짐)

```bash
git commit -m "feat!: 사원 데이터 구조 변경

BREAKING CHANGE: employeesData 스키마가 변경되었습니다.
- 'role' 필드가 'position'으로 변경
- 'dept' 필드가 'team'으로 변경

마이그레이션 가이드:
1. LocalStorage 클리어
2. 앱 새로고침"
```

### 2.4 스코프 사용 (선택사항)

```bash
# 페이지별
git commit -m "feat(dashboard): 통계 차트 추가"
git commit -m "fix(consultation): 키워드 태깅 오류 수정"

# 컴포넌트별
git commit -m "refactor(modal): AddEmployeeModal 컴포넌트 분리"
git commit -m "style(button): 버튼 컴포넌트 Tailwind 클래스 정리"

# 기능별
git commit -m "feat(auth): JWT 토큰 인증 구현"
git commit -m "perf(stt): STT 처리 성능 개선"
```

---

## 3. PR 프로세스

### 3.1 PR 생성 전 체크리스트

```bash
# 1. 최신 develop 코드 병합
git checkout develop
git pull origin develop
git checkout feature/my-feature
git merge develop

# 2. 충돌 해결 (있는 경우)
# 3. 로컬 테스트
npm run dev
npm run build
npm run lint

# 4. 커밋 정리 (필요시)
git rebase -i develop

# 5. 원격 브랜치에 push
git push origin feature/my-feature
```

### 3.2 PR 템플릿

```markdown
## 📝 변경 사항

### 주요 내용
- 로그인 페이지 UI 구현
- 사번/비밀번호 인증 로직 추가
- LocalStorage 기반 세션 관리

### 변경된 파일
- `src/app/pages/LoginPage.tsx` (신규)
- `src/app/App.tsx` (라우트 추가)
- `src/styles/theme.css` (색상 추가)

## 🎯 목적

사용자가 사번과 비밀번호로 로그인할 수 있도록 구현

## 🧪 테스트 방법

1. `/login` 페이지 접속
2. 사번: `EMP-001`, 비밀번호: `0000` 입력
3. 로그인 버튼 클릭
4. 대시보드로 리다이렉트 확인

## 📸 스크린샷

![로그인 페이지](./screenshots/login-page.png)

## 📌 관련 이슈

- #123

## ✅ 체크리스트

- [x] 코드 린트 통과 (`npm run lint`)
- [x] 로컬 빌드 성공 (`npm run build`)
- [x] 반응형 디자인 확인 (모바일, 태블릿, 데스크톱)
- [x] 브라우저 테스트 (Chrome, Safari, Firefox)
- [x] 주석 및 문서 업데이트
- [x] console.log 제거
```

### 3.3 PR 제목 규칙

```bash
✅ 올바른 예시:
[feat] 로그인 페이지 구현
[fix] 사이드바 오버랩 이슈 해결
[docs] API 명세서 업데이트
[refactor] 칸반보드 컴포넌트 분리

❌ 잘못된 예시:
로그인 페이지
수정
Update
fix
```

### 3.4 PR 병합 규칙

**병합 방식**:
- ✅ **Squash and Merge** (권장): 커밋 히스토리 정리
- ⚠️ **Rebase and Merge**: 선형 히스토리 유지
- ❌ **Merge Commit**: 사용 금지

**병합 조건**:
- ✅ 최소 1명 이상의 Approve
- ✅ 모든 CI 테스트 통과
- ✅ 충돌 해결 완료
- ❌ Draft PR은 병합 불가

---

## 4. 코드 리뷰 가이드

### 4.1 리뷰어 체크리스트

#### 4.1.1 기능 동작
- [ ] 요구사항에 맞게 구현되었는가?
- [ ] 버그나 예외 상황이 없는가?
- [ ] 성능 이슈가 없는가?

#### 4.1.2 코드 품질
- [ ] 코딩 컨벤션을 준수하는가?
- [ ] 컴포넌트가 적절히 분리되었는가?
- [ ] 불필요한 코드가 없는가?
- [ ] console.log가 제거되었는가?

#### 4.1.3 타입 안정성
- [ ] TypeScript 타입이 명확한가?
- [ ] `any` 타입을 사용하지 않았는가?
- [ ] Props 인터페이스가 정의되었는가?

#### 4.1.4 스타일
- [ ] Tailwind 클래스 순서가 올바른가?
- [ ] 반응형 디자인이 적용되었는가?
- [ ] 프로젝트 색상을 사용하는가?

#### 4.1.5 문서
- [ ] 주석이 적절히 작성되었는가?
- [ ] README가 업데이트되었는가?

### 4.2 리뷰 코멘트 작성법

#### 4.2.1 건설적인 피드백

```markdown
✅ 좋은 예시:
"이 부분은 컴포넌트로 분리하는 것이 좋을 것 같습니다. 
재사용성이 높아지고 코드가 더 읽기 쉬워질 것 같아요.

제안:
- DashboardStats 컴포넌트 생성
- Props로 stats 데이터 전달"

❌ 나쁜 예시:
"이거 너무 길어요. 분리하세요."
"이렇게 하면 안 됩니다."
```

#### 4.2.2 리뷰 태그 사용

```markdown
[MUST] 반드시 수정 필요
[SUGGESTION] 제안 사항
[QUESTION] 질문
[NITS] 사소한 지적 (선택적 수정)
[PRAISE] 잘한 점
```

**예시**:
```markdown
[MUST] `any` 타입을 구체적인 타입으로 변경해주세요.

[SUGGESTION] 이 로직은 utils 함수로 분리하는 것이 좋을 것 같습니다.

[QUESTION] 이 useEffect가 무한 루프를 발생시키지 않을까요?

[NITS] 변수명을 더 명확하게 `userData` → `currentUser`로 변경하는 것은 어떨까요?

[PRAISE] 컴포넌트 분리가 정말 깔끔하네요! 👍
```

### 4.3 리뷰 응답 가이드

#### 4.3.1 수정 완료
```markdown
✅ 수정 완료했습니다. 커밋: abc1234
```

#### 4.3.2 동의하지 않는 경우
```markdown
이 부분은 다음 이유로 현재 방식을 유지하고 싶습니다:
1. 성능상 이점이 있음
2. 기존 코드와 일관성 유지

다른 의견이 있으시면 말씀해주세요.
```

#### 4.3.3 추후 작업 예정
```markdown
좋은 제안입니다! 이 부분은 별도 이슈로 생성하여 
다음 스프린트에 작업하는 것이 어떨까요?

이슈: #456
```

---

## 5. Git 명령어 가이드

### 5.1 자주 사용하는 명령어

```bash
# ========== 브랜치 관리 ==========

# 브랜치 목록 확인
git branch -a

# 브랜치 생성 및 이동
git checkout -b feature/new-feature

# 브랜치 이동
git checkout develop

# 브랜치 삭제
git branch -d feature/old-feature

# 원격 브랜치 삭제
git push origin --delete feature/old-feature

# ========== 커밋 관리 ==========

# 스테이징
git add .
git add src/app/pages/LoginPage.tsx

# 커밋
git commit -m "feat: 로그인 페이지 구현"

# 커밋 수정 (마지막 커밋)
git commit --amend -m "feat: 로그인 페이지 UI 구현"

# 커밋 취소 (파일은 유지)
git reset --soft HEAD~1

# 커밋 취소 (파일도 되돌림)
git reset --hard HEAD~1

# ========== 동기화 ==========

# 최신 코드 가져오기
git pull origin develop

# 원격에 푸시
git push origin feature/my-feature

# 강제 푸시 (주의!)
git push origin feature/my-feature --force

# ========== 병합 ==========

# develop 브랜치 병합
git merge develop

# 충돌 해결 후
git add .
git commit -m "merge: develop 브랜치 병합"

# Rebase
git rebase develop

# Rebase 중단
git rebase --abort

# ========== 상태 확인 ==========

# 변경 파일 확인
git status

# 변경 내용 확인
git diff

# 커밋 히스토리 확인
git log --oneline --graph --all

# 특정 파일 히스토리
git log src/app/pages/LoginPage.tsx
```

### 5.2 유용한 Git 설정

```bash
# 사용자 정보 설정
git config --global user.name "홍길동"
git config --global user.email "hong@teddycard.com"

# 기본 에디터 설정
git config --global core.editor "code --wait"

# 줄바꿈 설정 (Windows)
git config --global core.autocrlf true

# 줄바꿈 설정 (Mac/Linux)
git config --global core.autocrlf input

# Git Alias 설정
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.cm commit
git config --global alias.lg "log --oneline --graph --all"
```

### 5.3 충돌 해결

```bash
# 1. 충돌 발생 시 상태 확인
git status

# 2. 충돌 파일 수정 (에디터에서)
# <<<<<<< HEAD
# 현재 브랜치 코드
# =======
# 병합하려는 브랜치 코드
# >>>>>>> feature/my-feature

# 3. 충돌 해결 후 스테이징
git add src/app/pages/ConflictedFile.tsx

# 4. 병합 완료
git commit -m "merge: 충돌 해결 및 develop 병합"
```

### 5.4 Stash 활용

```bash
# 현재 작업 임시 저장
git stash

# Stash 목록 확인
git stash list

# Stash 복원
git stash pop

# 특정 Stash 복원
git stash apply stash@{0}

# Stash 삭제
git stash drop stash@{0}

# 모든 Stash 삭제
git stash clear
```

---

## 6. 트러블슈팅

### 6.1 잘못된 브랜치에 커밋한 경우

```bash
# 1. 커밋을 Stash로 저장
git reset --soft HEAD~1
git stash

# 2. 올바른 브랜치로 이동
git checkout feature/correct-branch

# 3. Stash 복원
git stash pop

# 4. 다시 커밋
git add .
git commit -m "feat: 올바른 브랜치에 커밋"
```

### 6.2 실수로 main에 직접 푸시한 경우

```bash
# ⚠️ 주의: 팀원과 상의 후 진행

# 1. 로컬에서 되돌리기
git checkout main
git reset --hard HEAD~1

# 2. 강제 푸시 (위험!)
git push origin main --force

# 3. 올바른 프로세스로 다시 진행
git checkout develop
git checkout -b feature/my-feature
# ... 작업 후 PR
```

### 6.3 커밋 메시지 수정

```bash
# 마지막 커밋 메시지 수정
git commit --amend -m "feat: 수정된 커밋 메시지"

# 이미 푸시한 경우 (강제 푸시 필요)
git push origin feature/my-feature --force
```

---

## 7. 요약 체크리스트

### 브랜치
- [ ] `feature/`, `bugfix/`, `hotfix/`, `docs/` 접두사 사용
- [ ] develop에서 브랜치 생성
- [ ] 작업 완료 후 develop으로 PR

### 커밋
- [ ] Conventional Commits 형식 준수
- [ ] 명확하고 간결한 제목
- [ ] 필요시 본문 작성
- [ ] console.log 제거

### PR
- [ ] PR 템플릿 작성
- [ ] 최소 1명 Approve
- [ ] CI 테스트 통과
- [ ] Squash and Merge

### 코드 리뷰
- [ ] 건설적인 피드백
- [ ] 태그 사용 ([MUST], [SUGGESTION] 등)
- [ ] 빠른 응답

---

**이전 문서**: [24_코딩_컨벤션.md](./24_코딩_컨벤션.md)  
**다음 문서**: [26_테스트_가이드.md](./26_테스트_가이드.md)
