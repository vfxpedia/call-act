/**
 * 튜토리얼 말풍선 위치 설정
 *
 * 📐 기준 해상도: 1920×1080 (2K)
 * 🎯 지원 범위: 1366×768 ~ 3840×2160 (4K)
 *
 * ===== 수정 방법 =====
 *
 * 1. offsetY (세로 위치)
 *    - 양수 (+) : 아래로 이동 ↓
 *    - 음수 (-) : 위로 이동 ↑
 *    - 예: offsetY: -100 → 타겟 100px 위에 배치
 *
 * 2. offsetX (가로 위치)
 *    - 양수 (+) : 오른쪽으로 이동 →
 *    - 음수 (-) : 왼쪽으로 이동 ←
 *    - 예: offsetX: 50 → 타겟에서 50px 오른쪽
 *
 * 3. useTargetSize (타겟 크기 기반 계산)
 *    - true: 타겟 높이/너비를 기준으로 계산 (권장)
 *    - false: 고정 픽셀 사용
 *
 * 4. scaleWithViewport (뷰포트 스케일링)
 *    - true: 화면 크기에 비례하여 자동 확대/축소 (4K 대응)
 *    - false: 고정 픽셀 유지
 */

export interface TooltipOffset {
  offsetY?: number; // 세로 오프셋 (px)
  offsetX?: number; // 가로 오프셋 (px)
  useTargetSize?: boolean; // 타겟 크기 기반 계산 여부
  scaleWithViewport?: boolean; // 뷰포트 스케일링 여부
  minOffset?: number; // 최소 오프셋 (px)
  maxOffset?: number; // 최대 오프셋 (px)
}

/**
 * 📍 Phase별 말풍선 위치 설정
 */
export const tutorialOffsets: Record<string, TooltipOffset> = {
  // ==========================================
  // Phase 1: 대기 중 (통화 시작 전)
  // ==========================================

  "call-action-button": {
    offsetY: 35,
    offsetX: 0, // ⭐ 초기화 - 기본 위치 사용
    useTargetSize: false,
    scaleWithViewport: true,
  },

  "waiting-call-list": {
    offsetY: 35, // ⭐ 초기화 - 기본 위치 사용
    offsetX: 0, // ⭐ 초기화 - 기본 위치 사용
    useTargetSize: false,
    scaleWithViewport: true,
  },

  "scenario-selector": {
    offsetY: 0, // 🎯 타겟 위로 0px
    offsetX: 100, // 🎯 가로 중앙
    useTargetSize: false, // 고정 픽셀 사용
    scaleWithViewport: true, // 4K에서 자동 확대
  },

  // ==========================================
  // Phase 2: 통화 중
  // ==========================================

  "customer-info-card": {
    offsetY: 0,
    offsetX: 0, // 🎯 카드 오른쪽 0px
    useTargetSize: false,
    scaleWithViewport: true,
  },

  "stt-area": {
    offsetY: 0, // 🎯 타겟 아래 0px (타겟 높이 + 여백)
    offsetX: 0,
    useTargetSize: true, // 타겟 높이 기반
    scaleWithViewport: true,
  },

  "keyword-area": {
    offsetY: 0,
    offsetX: 0,
    useTargetSize: true,
    scaleWithViewport: true,
  },

  "current-cards-area": {
    offsetY: 0, // 🎯 카드 영역 아래 0px
    offsetX: 0,
    useTargetSize: true,
    scaleWithViewport: true,
  },

  "info-cards-area": {
    offsetY: 0, // 🎯 카드 영역이므로 여백 더 크게
    offsetX: 0,
    useTargetSize: true,
    scaleWithViewport: true,
  },

  "next-cards-area": {
    offsetY: 50,
    offsetX: 0,
    useTargetSize: false,
    scaleWithViewport: true,
  },

  "ai-search-area": {
    offsetY: 45,
    offsetX: 0,
    useTargetSize: false,
    scaleWithViewport: true,
  },

  "memo-area": {
    offsetY: 0,
    offsetX: 0,
    useTargetSize: false,
    scaleWithViewport: true,
  },

  "end-call-button": {
    offsetY: 30,
    offsetX: 0,
    useTargetSize: false,
    scaleWithViewport: true,
  },

  // ==========================================
  // 교육 시뮬레이션 페이지
  // ==========================================

  "sim-best-practices-section": {
    offsetY: 0,
    offsetX: 0,
    useTargetSize: false,
    scaleWithViewport: true,
  },

  "sim-basic-scenarios-section": {
    offsetY: 0,
    offsetX: 0,
    useTargetSize: false,
    scaleWithViewport: true,
  },

  "sim-recent-section": {
    offsetY: 0,
    offsetX: 0,
    useTargetSize: false,
    scaleWithViewport: true,
  },

  // ==========================================
  // Phase 3: 후처리
  // ==========================================

  "acw-transcript": {
    offsetY: 0,
    offsetX: 0,
    useTargetSize: false,
    scaleWithViewport: true,
  },

  "acw-docs": {
    offsetY: 0,
    offsetX: 0,
    useTargetSize: false,
    scaleWithViewport: true,
  },

  "acw-document-area": {
    offsetY: 0,
    offsetX: 0,
    useTargetSize: true,
    scaleWithViewport: true,
  },

  "acw-memo-area": {
    offsetY: 70,
    offsetX: 0,
    useTargetSize: false,
    scaleWithViewport: true,
  },

  "acw-save-button": {
    offsetY: 0, // 🎯 버튼 아래 고정 여백
    offsetX: -100,
    useTargetSize: false,
    scaleWithViewport: true,
  },
};

/**
 * 📐 뷰포트 스케일링 계산
 *
 * 기준: 1920×1080 (2K)
 * 자동 스케일: 4K에서 2배 확대
 */
export function getViewportScale(): number {
  const baseWidth = 1920;
  const cssZoom = parseFloat(getComputedStyle(document.documentElement).zoom) || 1;
  // CSS zoom 적용 시 window.innerWidth가 논리적 뷰포트로 변경될 수 있으므로
  // 물리적 뷰포트 너비로 정규화
  const currentWidth = window.innerWidth * cssZoom;

  // 최소 0.8배 ~ 최대 2.0배 스케일
  return Math.min(Math.max(currentWidth / baseWidth, 0.8), 2.0);
}

/**
 * 🎯 최종 오프셋 계산 (모든 로직 통합)
 */
export function calculateOffset(
  targetId: string,
  rect: DOMRect,
  axis: "x" | "y",
): number {
  const config = tutorialOffsets[targetId];
  if (!config) return 0;

  const isY = axis === "y";
  let baseOffset = isY
    ? config.offsetY || 0
    : config.offsetX || 0;

  // 1️⃣ 타겟 크기 기반 계산
  if (config.useTargetSize && baseOffset !== 0) {
    const targetSize = isY ? rect.height : rect.width;
    baseOffset = targetSize + Math.abs(baseOffset);
    // 음수면 다시 음수로
    if (
      (isY && config.offsetY! < 0) ||
      (!isY && config.offsetX! < 0)
    ) {
      baseOffset = -baseOffset;
    }
  }

  // 2️⃣ 뷰포트 스케일링 (4K 대응)
  if (config.scaleWithViewport) {
    const scale = getViewportScale();
    baseOffset = baseOffset * scale;
  }

  // 3️⃣ 최소/최대값 제한
  if (
    config.minOffset !== undefined &&
    Math.abs(baseOffset) < config.minOffset
  ) {
    baseOffset = config.minOffset * Math.sign(baseOffset || 1);
  }
  if (
    config.maxOffset !== undefined &&
    Math.abs(baseOffset) > config.maxOffset
  ) {
    baseOffset = config.maxOffset * Math.sign(baseOffset || 1);
  }

  return baseOffset;
}