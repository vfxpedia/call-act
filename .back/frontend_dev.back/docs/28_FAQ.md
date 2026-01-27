# 28. FAQ (자주 묻는 질문)

> **CALL:ACT 프로젝트의 자주 묻는 질문 및 답변**

## 목차
- [1. 일반 질문](#1-일반-질문)
- [2. 개발 환경 관련](#2-개발-환경-관련)
- [3. 기능 관련](#3-기능-관련)
- [4. 데이터 관련](#4-데이터-관련)
- [5. 성능 관련](#5-성능-관련)
- [6. 배포 관련](#6-배포-관련)

---

## 1. 일반 질문

### Q1. CALL:ACT가 무엇인가요?

**A:** CALL:ACT는 카드사 상담사를 위한 AI 기반 실시간 상담 지원 시스템입니다. 

**핵심 기능**:
- 📞 **실시간 STT**: 음성을 텍스트로 실시간 변환
- 🏷️ **키워드 태깅**: 대화에서 중요 키워드 자동 추출
- 📋 **칸반보드**: 상황에 맞는 문서를 카드 형태로 제공
- 🤖 **AI 요약**: 상담 종료 후 자동 요약 생성

**목표**: 상담사의 업무 효율 30% 향상, FCR 95% 달성

---

### Q2. 현재 개발 단계는 어디까지인가요?

**A:** 현재 **Phase 5 (문서화)** 진행 중입니다.

| Phase | 내용 | 상태 |
|-------|------|------|
| Phase 1-2 | 기본 구조 및 페이지 구현 | ✅ 완료 |
| Phase 3 | 칸반보드 및 데이터 확장 | ✅ 완료 |
| Phase 4 | fullText 약관 확장 | ✅ 완료 |
| **Phase 5** | **문서화** | 🔄 **진행 중** |
| Phase 6 | 백엔드 연동 | 📅 예정 |
| Phase 7 | STT API 연동 | 📅 예정 |

**현재 MVP 상태**: 프론트엔드 100% 완성, Mock Data 기반 동작

---

### Q3. 어떤 기술 스택을 사용하나요?

**A:** 

**프론트엔드**:
- React 18 + TypeScript
- Vite (빌드 도구)
- Tailwind CSS v4
- shadcn/ui (UI 컴포넌트)
- Motion/Framer Motion (애니메이션)
- React Router (라우팅)

**백엔드** (Phase 6에서 도입 예정):
- FastAPI (Python)
- PostgreSQL + pgvector
- OpenAI API (RAG)

**배포** (Phase 8):
- Vercel (프론트엔드)
- Railway (백엔드)

---

### Q4. 라이선스는 무엇인가요?

**A:** 현재는 **비공개 프로젝트**입니다. 

추후 오픈소스로 전환할 계획이 있으며, MIT 라이선스를 고려 중입니다.

---

## 2. 개발 환경 관련

### Q5. 개발 환경을 어떻게 설정하나요?

**A:**

```bash
# 1. Node.js 18+ 설치 확인
node -v  # v18.0.0 이상

# 2. 프로젝트 클론
git clone <repository-url>
cd call-act

# 3. 의존성 설치
npm install

# 4. 개발 서버 실행
npm run dev

# 5. 브라우저 열기
# http://localhost:5173
```

**문서**: [02_빠른_시작_가이드.md](./02_빠른_시작_가이드.md)

---

### Q6. 포트가 이미 사용 중이라고 나옵니다.

**A:** Vite 기본 포트(5173)가 사용 중인 경우입니다.

**해결 방법**:

```bash
# 방법 1: 포트를 사용하는 프로세스 종료
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:5173 | xargs kill

# 방법 2: 다른 포트로 실행
npm run dev -- --port 3000
```

---

### Q7. `npm install` 중 오류가 발생합니다.

**A:** 

**일반적인 원인**:
1. Node.js 버전이 낮음 (18+ 필요)
2. 네트워크 오류
3. npm 캐시 오염

**해결 방법**:

```bash
# 1. Node.js 버전 확인
node -v  # 18.0.0 이상인지 확인

# 2. npm 캐시 클리어
npm cache clean --force

# 3. node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install

# 4. 그래도 안 되면 Yarn 사용
npm install -g yarn
yarn install
```

---

### Q8. TypeScript 오류가 계속 발생합니다.

**A:**

**일반적인 원인**:
1. 타입 정의 파일 누락
2. `any` 타입 사용
3. Props 인터페이스 미정의

**해결 방법**:

```bash
# 1. TypeScript 버전 확인
npx tsc --version

# 2. 타입 체크 실행
npm run type-check

# 3. VSCode에서 TypeScript 서버 재시작
# Ctrl+Shift+P → "TypeScript: Restart TS Server"
```

**코딩 컨벤션**: [24_코딩_컨벤션.md](./24_코딩_컨벤션.md)

---

## 3. 기능 관련

### Q9. 로그인 계정은 무엇인가요?

**A:**

| 사번 | 비밀번호 | 역할 | 설명 |
|------|----------|------|------|
| `ADMIN-001` | `0000` | 관리자 | 모든 기능 접근 가능 |
| `EMP-001` | `0000` | 상담사 | 일반 사원 (김민수) |
| `EMP-002` | `0000` | 상담사 | 일반 사원 (이영희) |
| `EMP-003` ~ `EMP-050` | `0000` | 상담사 | mockData의 모든 사원 |

**참고**: 모든 계정의 기본 비밀번호는 `0000`입니다.

---

### Q10. 실시간 상담 시뮬레이션이 동작하지 않습니다.

**A:**

**체크리스트**:
1. 대기 콜 선택했는지 확인
2. "상담 시작" 버튼 클릭했는지 확인
3. STT 메시지가 나타나는지 확인 (2초 간격)

**디버깅**:

```javascript
// 브라우저 콘솔에서 확인
console.log('현재 시나리오:', currentScenario);
console.log('STT 메시지:', sttMessages);
```

**관련 파일**: `/src/app/pages/RealTimeConsultationPage.tsx`

---

### Q11. 칸반보드가 Step 전환이 안 됩니다.

**A:**

**원인**: Step 전환 조건이 충족되지 않았습니다.

**Step 전환 조건**:
```typescript
// 현재 Step의 모든 키워드가 태깅되어야 다음 Step으로 전환
const stepKeywords = currentStep.keywords.map(k => k.text);
const taggedKeywords = keywords.map(k => k.text);

const allTagged = stepKeywords.every(k => taggedKeywords.includes(k));
```

**확인 방법**:
1. 현재 Step 키워드 확인 (화면 우측 상단)
2. 태깅된 키워드와 비교
3. 부족한 키워드가 있으면 STT 메시지에 해당 단어가 나올 때까지 대기

**강제 전환** (개발 모드):
```javascript
// 브라우저 콘솔에서
setCurrentStepIndex(1);  // Step 2로 전환
setCurrentStepIndex(2);  // Step 3으로 전환
```

---

### Q12. 사원을 추가했는데 새로고침하면 사라집니다.

**A:**

**원인**: LocalStorage 동기화 문제

**해결 방법**:

```typescript
// AddEmployeeModal에서 사원 추가 후 LocalStorage 저장 확인
const handleAdd = (newEmployee: Employee) => {
  const updated = [...employees, newEmployee];
  setEmployees(updated);
  
  // LocalStorage에 저장 (이 부분이 누락되었는지 확인)
  localStorage.setItem('employees', JSON.stringify(updated));
};
```

**확인**:
```javascript
// 브라우저 콘솔에서
const employees = JSON.parse(localStorage.getItem('employees'));
console.log('사원 수:', employees.length);
```

---

### Q13. 모달이 열리지 않습니다.

**A:**

**일반적인 원인**:
1. 상태 관리 오류 (`isOpen` 상태)
2. z-index 충돌
3. Dialog 컴포넌트 import 누락

**해결 방법**:

```tsx
// 1. 상태 확인
const [isOpen, setIsOpen] = useState(false);

// 2. Dialog 컴포넌트 확인
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';

// 3. z-index 확인 (Dialog는 z-50)
<Dialog open={isOpen} onOpenChange={setIsOpen}>
  <DialogContent className="z-50">
    {/* ... */}
  </DialogContent>
</Dialog>
```

---

## 4. 데이터 관련

### Q14. Mock Data를 어떻게 수정하나요?

**A:**

**파일 위치**: `/src/data/mockData.ts`

**예시**:

```typescript
// 사원 추가
export const employeesData: Employee[] = [
  // 기존 사원들...
  {
    id: 'EMP-051',
    name: '새사원',
    team: '상담1팀',
    position: '사원',
    email: 'newsaewon@teddycard.com',
    phone: '010-9999-9999',
    status: 'active',
    joinDate: '2025-01-13',
    rank: 51,
    consultations: 0,
    fcr: 0,
    avgTime: '0:00',
    trend: 'same'
  }
];
```

**주의**: Mock Data 수정 후 LocalStorage 클리어 필요
```javascript
localStorage.clear();
location.reload();
```

---

### Q15. LocalStorage를 초기화하려면?

**A:**

**방법 1: 브라우저 콘솔**
```javascript
localStorage.clear();
location.reload();
```

**방법 2: 개발자 도구**
1. Chrome DevTools 열기 (F12)
2. Application 탭
3. Storage > Local Storage
4. 해당 도메인 우클릭 > Clear

**방법 3: 코드에서 초기화**
```typescript
// 특정 키만 삭제
localStorage.removeItem('employees');

// 전체 삭제
localStorage.clear();
```

---

### Q16. employeesData가 50명보다 적게 나옵니다.

**A:**

**원인**: LocalStorage에 50명 미만의 데이터가 저장되어 있습니다.

**자동 복구 로직**:
```typescript
// LoginPage.tsx, EmployeesPage.tsx 등에 구현됨
const savedEmployees = localStorage.getItem('employees');
if (savedEmployees) {
  const parsedEmployees = JSON.parse(savedEmployees);
  
  // 50명 미만이면 mockData로 초기화
  if (parsedEmployees.length < 50) {
    localStorage.setItem('employees', JSON.stringify(employeesData));
  }
}
```

**수동 복구**:
```javascript
// 브라우저 콘솔에서
localStorage.removeItem('employees');
location.reload();
```

---

### Q17. 칸반보드 카드를 추가하려면?

**A:**

**파일**: `/src/data/mockData.ts`

```typescript
// scenariosData에서 해당 시나리오 찾기
{
  category: '카드분실',
  steps: [
    {
      id: 'card-loss-step-1',
      name: '문제 파악',
      currentSituationCards: [
        // 새 카드 추가
        {
          id: 'new-card-001',
          title: '새로운 카드 제목',
          summary: '한 줄 요약',
          fullText: `
제XX조 (제목)
① 조항 1
② 조항 2
          `.trim(),
          requiredChecks: ['확인 사항 1', '확인 사항 2'],
          exceptions: ['예외 사항 1'],
          systemPath: '시스템 > 메뉴 > 하위메뉴',
          regulation: '카드업무 준칙 제XX조',
          category: '카드분실',
          priority: 'high',
          relatedKeywords: ['분실', '카드']
        }
      ],
      nextStepCards: [/* ... */]
    }
  ]
}
```

**주의**: 카드 추가 후 LocalStorage 클리어 필요

---

## 5. 성능 관련

### Q18. 페이지 로딩이 느립니다.

**A:**

**일반적인 원인**:
1. 큰 이미지 파일
2. 불필요한 리렌더링
3. 초기 데이터 로딩

**해결 방법**:

```typescript
// 1. 이미지 최적화
// - WebP 포맷 사용
// - 이미지 압축 (TinyPNG 등)

// 2. React.memo 사용
export default React.memo(ExpensiveComponent);

// 3. useMemo, useCallback 사용
const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);
const memoizedCallback = useCallback(() => doSomething(a, b), [a, b]);

// 4. Lazy Loading
const LazyComponent = React.lazy(() => import('./LazyComponent'));
```

**성능 측정**:
```bash
# Lighthouse 실행
npm run build
npx serve -s dist
# Chrome DevTools > Lighthouse > Analyze
```

---

### Q19. 칸반보드 애니메이션이 끊깁니다.

**A:**

**원인**: 
1. 하드웨어 가속 미지원
2. 너무 많은 DOM 요소
3. Motion 설정 문제

**해결 방법**:

```tsx
// 1. transform 사용 (GPU 가속)
<motion.div
  initial={{ x: '100%' }}  // ✅ Good
  // initial={{ left: '100%' }}  // ❌ Bad (layout 속성)
  animate={{ x: 0 }}
  transition={{ duration: 0.5, ease: 'easeOut' }}
>

// 2. will-change 추가
<motion.div
  style={{ willChange: 'transform' }}
>

// 3. 애니메이션 간소화 (60 FPS 목표)
transition={{ duration: 0.3 }}  // 0.5초 → 0.3초
```

---

### Q20. 메모리 누수가 발생합니다.

**A:**

**일반적인 원인**:
1. useEffect cleanup 누락
2. setInterval/setTimeout cleanup 누락
3. 이벤트 리스너 제거 안 함

**해결 방법**:

```typescript
// 1. useEffect cleanup
useEffect(() => {
  const interval = setInterval(() => {
    // ...
  }, 1000);
  
  return () => clearInterval(interval);  // ✅ Cleanup
}, []);

// 2. 이벤트 리스너 cleanup
useEffect(() => {
  const handleResize = () => { /* ... */ };
  window.addEventListener('resize', handleResize);
  
  return () => window.removeEventListener('resize', handleResize);  // ✅ Cleanup
}, []);

// 3. 컴포넌트 언마운트 시 상태 업데이트 방지
useEffect(() => {
  let isMounted = true;
  
  fetchData().then(data => {
    if (isMounted) {
      setData(data);  // ✅ 마운트된 경우만 업데이트
    }
  });
  
  return () => { isMounted = false; };
}, []);
```

---

## 6. 배포 관련

### Q21. 프로덕션 빌드가 실패합니다.

**A:**

**일반적인 원인**:
1. TypeScript 오류
2. 사용하지 않는 import
3. 환경 변수 누락

**해결 방법**:

```bash
# 1. 타입 체크
npm run type-check

# 2. Lint 실행
npm run lint

# 3. 빌드 실행
npm run build

# 4. 빌드 결과 미리보기
npm run preview
```

**에러 메시지 확인**:
```bash
# 자세한 에러 메시지 출력
npm run build -- --debug
```

---

### Q22. Vercel 배포 시 404 오류가 발생합니다.

**A:**

**원인**: React Router의 SPA 라우팅 설정 누락

**해결 방법**:

**1. `vercel.json` 파일 생성**:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

**2. Vercel 대시보드 설정**:
- Settings > General > Build & Development Settings
- Framework Preset: `Vite`
- Build Command: `npm run build`
- Output Directory: `dist`

---

### Q23. 환경 변수를 어떻게 설정하나요?

**A:**

**개발 환경**:

`.env` 파일 생성:
```bash
VITE_API_URL=http://localhost:8000
VITE_OPENAI_API_KEY=sk-...
```

사용:
```typescript
const apiUrl = import.meta.env.VITE_API_URL;
```

**프로덕션 환경 (Vercel)**:

1. Vercel 대시보드 > Settings > Environment Variables
2. 변수 추가:
   - Name: `VITE_API_URL`
   - Value: `https://api.example.com`
3. Redeploy

**주의**: 
- Vite 환경 변수는 `VITE_` 접두사 필수
- 민감한 정보는 `.env`에 저장하고 `.gitignore`에 추가

---

### Q24. HTTPS를 로컬에서 테스트하려면?

**A:**

**방법 1: mkcert 사용**:
```bash
# 1. mkcert 설치
brew install mkcert  # Mac
choco install mkcert  # Windows

# 2. 로컬 CA 생성
mkcert -install

# 3. 인증서 생성
mkcert localhost

# 4. Vite 설정 수정 (vite.config.ts)
import { defineConfig } from 'vite';
import fs from 'fs';

export default defineConfig({
  server: {
    https: {
      key: fs.readFileSync('./localhost-key.pem'),
      cert: fs.readFileSync('./localhost.pem')
    }
  }
});

# 5. 개발 서버 실행
npm run dev
# https://localhost:5173
```

---

## 7. 기타 질문

### Q25. 문서가 너무 많아서 어디서부터 읽어야 할지 모르겠습니다.

**A:**

**신규 개발자 추천 순서**:

1. **[README.md](../README.md)** - 프로젝트 개요
2. **[02_빠른_시작_가이드.md](./02_빠른_시작_가이드.md)** - 개발 환경 설정
3. **[03_시스템_아키텍처.md](./03_시스템_아키텍처.md)** - 전체 구조 이해
4. **[09_페이지별_구현_상세.md](./09_페이지별_구현_상세.md)** - 페이지 기능
5. **[24_코딩_컨벤션.md](./24_코딩_컨벤션.md)** - 코딩 규칙

**특정 작업 시**:
- 새 기능 개발 → **10_컴포넌트_가이드.md**
- 칸반보드 수정 → **14_칸반보드_시스템.md**
- 데이터 추가 → **07_MockData_구조.md**
- 배포 → **21_배포_가이드.md**

---

### Q26. 기여하고 싶은데 어떻게 해야 하나요?

**A:**

**기여 프로세스**:

1. **이슈 생성**
   - GitHub Issues에서 새 이슈 생성
   - 버그 리포트 또는 기능 제안

2. **브랜치 생성**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature
   ```

3. **개발 및 커밋**
   ```bash
   git add .
   git commit -m "feat: 새로운 기능 추가"
   ```

4. **PR 생성**
   - GitHub에서 Pull Request 생성
   - PR 템플릿 작성
   - 리뷰 대기

**상세 가이드**: [25_Git_워크플로우.md](./25_Git_워크플로우.md)

---

### Q27. 버그를 발견했습니다. 어떻게 해야 하나요?

**A:**

**버그 리포트 방법**:

1. **GitHub Issues에 버그 리포트 작성**:
   ```markdown
   ## 버그 설명
   사이드바가 모바일에서 콘텐츠와 겹칩니다.
   
   ## 재현 방법
   1. 모바일 (375px)로 축소
   2. 사이드바 열기
   3. 콘텐츠 영역 클릭
   
   ## 예상 동작
   사이드바가 자동으로 닫혀야 합니다.
   
   ## 실제 동작
   사이드바가 콘텐츠와 겹쳐서 표시됩니다.
   
   ## 스크린샷
   [첨부]
   
   ## 환경
   - OS: macOS 14
   - 브라우저: Chrome 120
   - 화면 크기: 375px
   ```

2. **라벨 추가**: `bug`, `high-priority` 등

3. **담당자 지정** (선택)

---

### Q28. 새로운 기능을 제안하고 싶습니다.

**A:**

**기능 제안 방법**:

1. **GitHub Issues에 기능 제안 작성**:
   ```markdown
   ## 기능 설명
   상담 이력 페이지에 엑셀 내보내기 기능 추가
   
   ## 동기
   관리자가 월간 상담 데이터를 분석하기 위해 엑셀로 내보내기가 필요합니다.
   
   ## 제안 구현
   - "엑셀 내보내기" 버튼 추가 (우측 상단)
   - react-csv 또는 xlsx 라이브러리 사용
   - 현재 필터링된 데이터만 내보내기
   
   ## 대안
   CSV 파일로 내보내기
   
   ## 추가 컨텍스트
   경쟁사 시스템에도 유사 기능 존재
   ```

2. **라벨 추가**: `enhancement`, `feature-request`

3. **토론 참여**

---

### Q29. 프로젝트에 대해 더 알고 싶습니다.

**A:**

**리소스**:

1. **문서**:
   - [README.md](../README.md) - 프로젝트 개요
   - [01_프로젝트_개요.md](./01_프로젝트_개요.md) - 상세 개요
   - [27_용어_사전.md](./27_용어_사전.md) - 용어 정리

2. **코드**:
   - `/src/app/pages` - 페이지 컴포넌트
   - `/src/data/mockData.ts` - Mock 데이터
   - `/docs` - 전체 문서 (30개+)

3. **문의**:
   - GitHub Discussions
   - 이메일: support@callact.com

---

### Q30. 라이선스 및 사용 조건은?

**A:**

**현재**: 비공개 프로젝트

**계획**: MIT 라이선스로 오픈소스 전환 예정

**사용 조건** (예정):
- ✅ 상업적 사용 가능
- ✅ 수정 및 재배포 가능
- ✅ 개인/기업 모두 사용 가능
- ⚠️ 저작권 표시 필수
- ⚠️ 무보증 (as-is 제공)

---

## 8. 요약

**FAQ 총 개수**: 30개

**카테고리별**:
- 일반 질문: 4개
- 개발 환경: 4개
- 기능 관련: 5개
- 데이터 관련: 4개
- 성능 관련: 3개
- 배포 관련: 4개
- 기타: 6개

**자주 찾는 질문 TOP 5**:
1. Q9: 로그인 계정
2. Q5: 개발 환경 설정
3. Q11: 칸반보드 Step 전환
4. Q14: Mock Data 수정
5. Q15: LocalStorage 초기화

**더 많은 도움이 필요하신가요?**
- [29_트러블슈팅.md](./29_트러블슈팅.md) 참고
- GitHub Issues에 질문 작성
- 팀원에게 문의

---

**이전 문서**: [27_용어_사전.md](./27_용어_사전.md)  
**다음 문서**: [29_트러블슈팅.md](./29_트러블슈팅.md)
