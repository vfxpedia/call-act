/**
 * 상담사 관련 유틸리티 함수
 */

export interface Employee {
  id: string;
  name: string;
  team?: string;
  position?: string;
  consultations?: number;
  fcr?: number;
  avgTime?: string;
  rank?: number;
  trend?: 'up' | 'same' | 'down';
  status?: 'active' | 'vacation' | 'inactive';
  joinDate?: string;
  email?: string;
  phone?: string;
}

/**
 * agent_id로 상담사 이름을 조회합니다.
 * @param agentId - 상담사 ID (예: 'EMP-001')
 * @param employees - 상담사 데이터 배열
 * @returns 상담사 이름 또는 agentId (찾지 못한 경우)
 */
export function getAgentName(agentId: string | undefined | null, employees: Employee[]): string {
  if (!agentId) {
    return '알 수 없음';
  }
  
  const employee = employees.find(emp => emp.id === agentId);
  return employee?.name || agentId;
}

/**
 * agent_id로 상담사 정보를 조회합니다.
 * @param agentId - 상담사 ID (예: 'EMP-001')
 * @param employees - 상담사 데이터 배열
 * @returns 상담사 정보 또는 null
 */
export function getEmployeeById(agentId: string | undefined | null, employees: Employee[]): Employee | null {
  if (!agentId) {
    return null;
  }
  
  return employees.find(emp => emp.id === agentId) || null;
}
