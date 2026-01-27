/**
 * 개인정보 마스킹 유틸리티 함수
 *
 * Toss CRM 방식: DB에는 실제 데이터 저장, 화면에는 마스킹 표시
 * 클릭 시 실명 노출 (3-5초) 기능과 함께 사용
 */

/**
 * 이름 마스킹
 * @param name 원본 이름 (예: "김민수")
 * @returns 마스킹된 이름 (예: "김*수")
 *
 * @example
 * maskName("김민수") // "김*수"
 * maskName("김민") // "김*"
 * maskName("K") // "K"
 */
export function maskName(name: string): string {
  if (!name) return '';
  if (name.length <= 1) return name;
  if (name.length === 2) return name[0] + '*';
  return name[0] + '*'.repeat(name.length - 2) + name.slice(-1);
}

/**
 * 전화번호 마스킹
 * @param phone 원본 전화번호 (예: "010-1234-5678")
 * @returns 마스킹된 전화번호 (예: "010-****-5678")
 *
 * @example
 * maskPhone("010-1234-5678") // "010-****-5678"
 * maskPhone("01012345678") // "010****5678"
 */
export function maskPhone(phone: string): string {
  if (!phone) return '';

  // 하이픈이 있는 경우: 010-1234-5678 → 010-****-5678
  if (phone.includes('-')) {
    return phone.replace(/(\d{3})-(\d{4})-(\d{4})/, '$1-****-$3');
  }

  // 하이픈이 없는 경우: 01012345678 → 010****5678
  if (phone.length >= 11) {
    return phone.slice(0, 3) + '****' + phone.slice(7);
  }

  return phone;
}

/**
 * 카드번호 마스킹 (마지막 4자리만 표시)
 * @param last4 카드번호 마지막 4자리 (예: "5678")
 * @returns 마스킹된 카드번호 (예: "****-****-****-5678")
 *
 * @example
 * maskCardNumber("5678") // "****-****-****-5678"
 */
export function maskCardNumber(last4: string): string {
  if (!last4) return '****-****-****-****';
  return `****-****-****-${last4}`;
}

/**
 * 카드번호 전체 마스킹
 * @param cardNumber 원본 카드번호 (예: "1234-5678-9012-3456")
 * @returns 마스킹된 카드번호 (예: "1234-****-****-3456")
 *
 * @example
 * maskFullCardNumber("1234-5678-9012-3456") // "1234-****-****-3456"
 */
export function maskFullCardNumber(cardNumber: string): string {
  if (!cardNumber) return '';

  // 하이픈이 있는 경우
  if (cardNumber.includes('-')) {
    const parts = cardNumber.split('-');
    if (parts.length === 4) {
      return `${parts[0]}-****-****-${parts[3]}`;
    }
  }

  // 하이픈이 없는 16자리인 경우
  if (cardNumber.length >= 16) {
    return cardNumber.slice(0, 4) + '-****-****-' + cardNumber.slice(-4);
  }

  return cardNumber;
}

/**
 * 이메일 마스킹
 * @param email 원본 이메일 (예: "user@example.com")
 * @returns 마스킹된 이메일 (예: "us**@example.com")
 *
 * @example
 * maskEmail("user@example.com") // "us**@example.com"
 * maskEmail("a@b.com") // "a@b.com"
 */
export function maskEmail(email: string): string {
  if (!email || !email.includes('@')) return email || '';

  const [localPart, domain] = email.split('@');

  if (localPart.length <= 2) {
    return email;
  }

  const visibleLength = Math.min(2, Math.floor(localPart.length / 2));
  const maskedLocal = localPart.slice(0, visibleLength) + '*'.repeat(localPart.length - visibleLength);

  return `${maskedLocal}@${domain}`;
}

/**
 * 주민등록번호 마스킹
 * @param ssn 원본 주민등록번호 (예: "900315-1234567")
 * @returns 마스킹된 주민등록번호 (예: "900315-*******")
 *
 * @example
 * maskSSN("900315-1234567") // "900315-*******"
 */
export function maskSSN(ssn: string): string {
  if (!ssn) return '';

  if (ssn.includes('-')) {
    const [front] = ssn.split('-');
    return `${front}-*******`;
  }

  if (ssn.length >= 13) {
    return ssn.slice(0, 6) + '-*******';
  }

  return ssn;
}

/**
 * 주소 마스킹 (상세주소 숨김)
 * @param address 원본 주소 (예: "서울시 강남구 테헤란로 123 아파트 101호")
 * @returns 마스킹된 주소 (예: "서울시 강남구 테헤란로 ***")
 *
 * @example
 * maskAddress("서울시 강남구 테헤란로 123 아파트 101호") // "서울시 강남구 테헤란로 ***"
 */
export function maskAddress(address: string): string {
  if (!address) return '';

  // 공백으로 분리하여 앞 3~4개 부분만 표시
  const parts = address.split(' ');
  if (parts.length <= 3) {
    return address;
  }

  // 시/구/동 까지만 표시
  const visibleParts = parts.slice(0, 3).join(' ');
  return `${visibleParts} ***`;
}

// ============================================================
// React Hook 및 컴포넌트용 유틸리티
// ============================================================

export interface MaskableValue {
  original: string;
  masked: string;
}

/**
 * 마스킹 가능한 값 객체 생성
 * @param original 원본 값
 * @param maskFn 마스킹 함수
 * @returns 원본과 마스킹된 값을 포함하는 객체
 *
 * @example
 * const name = createMaskableValue("김민수", maskName);
 * console.log(name.masked); // "김*수"
 * console.log(name.original); // "김민수"
 */
export function createMaskableValue(
  original: string,
  maskFn: (value: string) => string
): MaskableValue {
  return {
    original,
    masked: maskFn(original),
  };
}

/**
 * 고객 정보 마스킹 헬퍼
 * @param customer 고객 정보 객체
 * @returns 마스킹된 고객 정보
 */
export interface CustomerDisplay {
  id: string;
  name: string;
  phone: string;
  cardNumber: string;
  cardType: string;
  grade: string;
}

export interface MaskedCustomerDisplay {
  id: string;
  name: MaskableValue;
  phone: MaskableValue;
  cardNumber: MaskableValue;
  cardType: string;
  grade: string;
}

export function maskCustomerInfo(customer: CustomerDisplay): MaskedCustomerDisplay {
  return {
    id: customer.id,
    name: createMaskableValue(customer.name, maskName),
    phone: createMaskableValue(customer.phone, maskPhone),
    cardNumber: createMaskableValue(customer.cardNumber, (val) => {
      // 이미 부분 마스킹된 경우 그대로 반환
      if (val.includes('****')) return val;
      return maskFullCardNumber(val);
    }),
    cardType: customer.cardType,
    grade: customer.grade,
  };
}
