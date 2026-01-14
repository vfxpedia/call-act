import { useState, useEffect } from 'react';
import MainLayout from '../components/layout/MainLayout';
import { UserPlus, Edit2, Trash2, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { employeesData } from '../../data/mockData';
import AddEmployeeModal from '../components/modals/AddEmployeeModal';
import EditEmployeeModal from '../components/modals/EditEmployeeModal';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Pagination } from '../components/ui/Pagination';

const itemsPerPage = 20; // 페이지당 표시할 사원 수

export default function AdminManagePage() {
  const [employees, setEmployees] = useState(employeesData);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [teamFilter, setTeamFilter] = useState('전체');
  const [positionFilter, setPositionFilter] = useState('전체');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'vacation' | 'inactive'>('all');
  const [sortColumn, setSortColumn] = useState('id');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  // LocalStorage에서 사원 목록 불러오기
  useEffect(() => {
    const savedEmployees = localStorage.getItem('employees');
    let employeesToUse = employeesData;

    if (savedEmployees) {
      try {
        const parsedEmployees = JSON.parse(savedEmployees);
        
        // 50명보다 적으면 mockData로 초기화
        if (parsedEmployees.length < 50) {
          console.log('LocalStorage 데이터가 50명 미만입니다. mockData로 초기화합니다.');
          employeesToUse = employeesData;
        } else {
          employeesToUse = parsedEmployees;
        }
      } catch (e) {
        console.error('Failed to load employees', e);
        employeesToUse = employeesData;
      }
    }

    // 팀 이름 정규화 (띄워쓰기 제거: "상담 1팀" -> "상담1팀")
    const normalizedEmployees = employeesToUse.map((emp: any) => ({
      ...emp,
      team: emp.team.replace(/\s+/g, ''), // 모든 공백 제거
    }));

    setEmployees(normalizedEmployees);
    localStorage.setItem('employees', JSON.stringify(normalizedEmployees));
  }, []);

  // 사원 목록이 변경될 때마다 LocalStorage에 저장
  useEffect(() => {
    localStorage.setItem('employees', JSON.stringify(employees));
  }, [employees]);

  // 사원 추가
  const handleAddEmployee = (newEmployee: any) => {
    setEmployees(prev => [newEmployee, ...prev]);
  };

  // 사원 수정
  const handleEditEmployee = (updatedEmployee: any) => {
    setEmployees(prev => prev.map(emp => emp.id === updatedEmployee.id ? updatedEmployee : emp));
  };

  // 사원 삭제
  const handleDeleteEmployee = (id: string) => {
    if (confirm('정말 삭제하시겠습니까?')) {
      setEmployees(prev => prev.filter(emp => emp.id !== id));
    }
  };

  // 팀, 직급 목록 추출
  const teams = ['전체', ...Array.from(new Set(employees.map(emp => emp.team)))];
  const positions = ['전체', ...Array.from(new Set(employees.map(emp => emp.position)))];

  const filteredEmployees = employees.filter(emp => {
    const matchesSearch = emp.name.includes(searchTerm) || 
                          emp.id.includes(searchTerm) ||
                          emp.team.includes(searchTerm);
    return matchesSearch;
  });

  // 정렬 함수
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  // 정렬된 데이터
  const sortedEmployees = [...filteredEmployees].sort((a, b) => {
    let aValue: any = a[sortColumn as keyof typeof a];
    let bValue: any = b[sortColumn as keyof typeof b];

    if (sortDirection === 'asc') {
      if (typeof aValue === 'string') {
        return aValue.localeCompare(bValue);
      }
      return aValue - bValue;
    } else {
      if (typeof aValue === 'string') {
        return bValue.localeCompare(aValue);
      }
      return bValue - aValue;
    }
  });

  // 정렬 아이콘 렌더링
  const renderSortIcon = (column: string) => {
    // 화살표 아이콘 제거 (깔끔한 UI를 위해)
    return null;
  };

  // 페이징 처리
  const totalPages = Math.ceil(filteredEmployees.length / itemsPerPage);
  const currentEmployees = sortedEmployees.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  return (
    <MainLayout>
      <div className="h-[calc(100vh-60px)] flex flex-col p-3 gap-3 bg-[#F5F5F5] overflow-hidden">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-[#E0E0E0] p-3 flex-shrink-0">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
            <h1 className="text-lg font-bold text-[#333333]">사원 관리</h1>
            <Button className="bg-[#0047AB] hover:bg-[#003580] h-8 text-xs px-3 w-full sm:w-auto" onClick={() => setIsAddModalOpen(true)}>
              <UserPlus className="w-3.5 h-3.5 mr-1.5" />
              사원 추가
            </Button>
          </div>
          
          {/* 모든 필터를 하나의 행에 배치 - 모바일에서는 여러 줄로 자동 변경 */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Search */}
            <div className="flex-1 min-w-[180px] relative">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#999999]" />
              <Input 
                className="pl-8 h-8 text-xs placeholder:text-[10px]" 
                placeholder="사원명, 사번, 팀 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* 팀 필터 */}
            <Select value={teamFilter} onValueChange={setTeamFilter}>
              <SelectTrigger className="w-[110px] h-8 text-xs border-[#E0E0E0]">
                <SelectValue placeholder="팀 선택" />
              </SelectTrigger>
              <SelectContent>
                {teams.map(team => (
                  <SelectItem key={team} value={team} className="text-xs">{team}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* 직급 필터 */}
            <Select value={positionFilter} onValueChange={setPositionFilter}>
              <SelectTrigger className="w-[110px] h-8 text-xs border-[#E0E0E0]">
                <SelectValue placeholder="직급 선택" />
              </SelectTrigger>
              <SelectContent>
                {positions.map(position => (
                  <SelectItem key={position} value={position} className="text-xs">{position}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* 상태 필터 버튼들 */}
            <div className="flex gap-1.5">
              <Button
                variant={filterStatus === 'all' ? 'default' : 'outline'}
                onClick={() => setFilterStatus('all')}
                className={`h-8 text-xs px-2.5 ${filterStatus === 'all' ? 'bg-[#0047AB]' : ''}`}
              >
                전체
              </Button>
              <Button
                variant={filterStatus === 'active' ? 'default' : 'outline'}
                onClick={() => setFilterStatus('active')}
                className={`h-8 text-xs px-2.5 ${filterStatus === 'active' ? 'bg-[#34A853]' : ''}`}
              >
                재직
              </Button>
              <Button
                variant={filterStatus === 'vacation' ? 'default' : 'outline'}
                onClick={() => setFilterStatus('vacation')}
                className={`h-8 text-xs px-2.5 ${filterStatus === 'vacation' ? 'bg-[#FBBC04]' : ''}`}
              >
                휴가
              </Button>
              <Button
                variant={filterStatus === 'inactive' ? 'default' : 'outline'}
                onClick={() => setFilterStatus('inactive')}
                className={`h-8 text-xs px-2.5 ${filterStatus === 'inactive' ? 'bg-[#EA4335]' : ''}`}
              >
                비활성
              </Button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3 flex-shrink-0">
          <div className="bg-white rounded-lg shadow-sm p-2.5 text-center border border-[#E0E0E0]">
            <div className="text-xl font-bold text-[#0047AB] mb-0.5">
              {employees.length}
            </div>
            <div className="text-[10px] text-[#666666]">전체 사원</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-2.5 text-center border border-[#E0E0E0]">
            <div className="text-xl font-bold text-[#34A853] mb-0.5">
              {employees.filter(e => e.status === 'active').length}
            </div>
            <div className="text-[10px] text-[#666666]">재직 중</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-2.5 text-center border border-[#E0E0E0]">
            <div className="text-xl font-bold text-[#FBBC04] mb-0.5">
              {employees.filter(e => e.status === 'vacation').length}
            </div>
            <div className="text-[10px] text-[#666666]">휴가 중</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-2.5 text-center border border-[#E0E0E0]">
            <div className="text-xl font-bold text-[#EA4335] mb-0.5">
              {employees.filter(e => e.status === 'inactive').length}
            </div>
            <div className="text-[10px] text-[#666666]">비활성</div>
          </div>
        </div>

        {/* Employee Table/List */}
        <div className="flex-1 bg-white rounded-lg shadow-sm border border-[#E0E0E0] flex flex-col overflow-hidden min-h-0 flex-shrink-0">
          <div className="px-3 py-2 border-b border-[#E0E0E0] flex-shrink-0">
            <h2 className="text-sm font-bold text-[#333333]">
              사원 목록 ({filteredEmployees.length}명)
            </h2>
          </div>
          
          {/* 데스크톱 테이블 */}
          <div className="hidden lg:block flex-1 overflow-y-auto overflow-x-auto">
            <table className="w-full">
              <thead className="border-b-2 border-[#E0E0E0] sticky top-0 bg-white">
                <tr>
                  <th className="text-center text-[11px] font-semibold text-[#666666] py-2 px-3 w-[100px] cursor-pointer align-middle" onClick={() => handleSort('id')}>
                    사번 {renderSortIcon('id')}
                  </th>
                  <th className="text-center text-[11px] font-semibold text-[#666666] py-2 px-3 w-[100px] cursor-pointer align-middle" onClick={() => handleSort('name')}>
                    이름 {renderSortIcon('name')}
                  </th>
                  <th className="text-center text-[11px] font-semibold text-[#666666] py-2 px-3 w-[100px] cursor-pointer align-middle" onClick={() => handleSort('team')}>
                    소속 {renderSortIcon('team')}
                  </th>
                  <th className="text-center text-[11px] font-semibold text-[#666666] py-2 px-3 w-[80px] cursor-pointer align-middle" onClick={() => handleSort('position')}>
                    직급 {renderSortIcon('position')}
                  </th>
                  <th className="text-center text-[11px] font-semibold text-[#666666] py-2 px-3 w-[100px] cursor-pointer align-middle" onClick={() => handleSort('status')}>
                    상태 {renderSortIcon('status')}
                  </th>
                  <th className="text-center text-[11px] font-semibold text-[#666666] py-2 px-3 w-[180px] cursor-pointer align-middle" onClick={() => handleSort('email')}>
                    이메일 {renderSortIcon('email')}
                  </th>
                  <th className="text-center text-[11px] font-semibold text-[#666666] py-2 px-3 w-[120px] cursor-pointer align-middle" onClick={() => handleSort('phone')}>
                    연락처 {renderSortIcon('phone')}
                  </th>
                  <th className="text-center text-[11px] font-semibold text-[#666666] py-2 px-3 w-[100px] cursor-pointer align-middle" onClick={() => handleSort('joinDate')}>
                    입사일 {renderSortIcon('joinDate')}
                  </th>
                  <th className="text-center text-[11px] font-semibold text-[#666666] py-2 px-3 w-[120px] align-middle">관리</th>
                </tr>
              </thead>
              <tbody>
                {currentEmployees.map((emp) => (
                  <tr 
                    key={emp.id}
                    className="border-b border-[#F0F0F0] hover:bg-[#F8F9FA] transition-colors"
                  >
                    <td className="py-2 px-3 text-center align-middle">
                      <span className="text-xs text-[#666666] font-mono">{emp.id}</span>
                    </td>
                    <td className="py-2 px-3 text-center align-middle">
                      <span className="text-xs font-semibold text-[#333333]">{emp.name}</span>
                    </td>
                    <td className="py-2 px-3 text-center align-middle">
                      <span className="text-xs text-[#666666]">{emp.team}</span>
                    </td>
                    <td className="py-2 px-3 text-center align-middle">
                      <span className="text-xs px-2 py-1 bg-[#E8F1FC] text-[#0047AB] rounded">
                        {emp.position}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-center align-middle">
                      <div className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${
                        emp.status === 'active' ? 'bg-[#E8F5E9] text-[#34A853]' :
                        emp.status === 'vacation' ? 'bg-[#FFF9E6] text-[#FBBC04]' :
                        'bg-[#F5F5F5] text-[#999999]'
                      }`}>
                        {emp.status === 'active' ? '재직' : emp.status === 'vacation' ? '휴가' : '비활성'}
                      </div>
                    </td>
                    <td className="py-2 px-3 text-center align-middle">
                      <span className="text-xs text-[#666666]">{emp.email}</span>
                    </td>
                    <td className="py-2 px-3 text-center align-middle">
                      <span className="text-xs text-[#666666] font-mono">{emp.phone}</span>
                    </td>
                    <td className="py-2 px-3 text-center align-middle">
                      <span className="text-xs text-[#666666]">{emp.joinDate}</span>
                    </td>
                    <td className="py-2 px-3 align-middle">
                      <div className="flex items-center justify-center gap-2">
                        <Button variant="outline" size="sm" className="h-8" onClick={() => { setSelectedEmployee(emp); setIsEditModalOpen(true); }}>
                          <Edit2 className="w-3 h-3" />
                        </Button>
                        <Button variant="outline" size="sm" className="h-8 text-[#EA4335] hover:text-[#EA4335] hover:bg-[#FFEBEE]" onClick={() => handleDeleteEmployee(emp.id)}>
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* 모바일/태블릿 카드 뷰 */}
          <div className="lg:hidden flex-1 overflow-y-auto p-3">
            <div className="space-y-3">
              {currentEmployees.map((emp) => (
                <div 
                  key={emp.id}
                  className="bg-white border border-[#E0E0E0] rounded-lg p-3 hover:shadow-md transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-bold text-[#333333]">{emp.name}</span>
                        <span className="text-xs px-2 py-0.5 bg-[#E8F1FC] text-[#0047AB] rounded">
                          {emp.position}
                        </span>
                      </div>
                      <div className="text-[10px] text-[#999999] font-mono">{emp.id}</div>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-[10px] font-medium ${
                      emp.status === 'active' ? 'bg-[#E8F5E9] text-[#34A853]' :
                      emp.status === 'vacation' ? 'bg-[#FFF9E6] text-[#FBBC04]' :
                      'bg-[#F5F5F5] text-[#999999]'
                    }`}>
                      {emp.status === 'active' ? '재직' : emp.status === 'vacation' ? '휴가' : '비활성'}
                    </div>
                  </div>

                  <div className="space-y-1.5 mb-3">
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-[#999999] w-12">소속:</span>
                      <span className="text-[#333333]">{emp.team}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-[#999999] w-12">이메일:</span>
                      <span className="text-[#333333] truncate">{emp.email}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-[#999999] w-12">연락처:</span>
                      <span className="text-[#333333] font-mono">{emp.phone}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-[#999999] w-12">입사일:</span>
                      <span className="text-[#333333]">{emp.joinDate}</span>
                    </div>
                  </div>

                  <div className="flex gap-2 pt-2 border-t border-[#E0E0E0]">
                    <Button variant="outline" size="sm" className="flex-1 h-8 text-xs" onClick={() => { setSelectedEmployee(emp); setIsEditModalOpen(true); }}>
                      <Edit2 className="w-3 h-3 mr-1" />
                      수정
                    </Button>
                    <Button variant="outline" size="sm" className="flex-1 h-8 text-xs text-[#EA4335] hover:text-[#EA4335] hover:bg-[#FFEBEE]" onClick={() => handleDeleteEmployee(emp.id)}>
                      <Trash2 className="w-3 h-3 mr-1" />
                      삭제
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 페이징 버튼 */}
          <div className="px-3 py-2 border-t border-[#E0E0E0] flex-shrink-0">
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              totalItems={filteredEmployees.length}
              itemsPerPage={itemsPerPage}
            />
          </div>
        </div>
      </div>
      <AddEmployeeModal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} onAdd={handleAddEmployee} />
      <EditEmployeeModal isOpen={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} employee={selectedEmployee} onEdit={handleEditEmployee} />
    </MainLayout>
  );
}