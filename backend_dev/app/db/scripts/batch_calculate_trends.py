#!/usr/bin/env python
"""
Trend 계산 배치 Job

매일 12시에 실행하여 employees와 frequent_inquiries의 trend를 재계산합니다.

사용법:
    python batch_calculate_trends.py

스케줄 설정 (Windows Task Scheduler / Linux Cron):
    - Windows: 작업 스케줄러에서 매일 12:00에 실행되도록 설정
    - Linux: crontab -e 에서 "0 12 * * * /path/to/python batch_calculate_trends.py" 추가

환경:
    - .env 파일에 DB 연결 정보가 필요합니다:
      DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

최종 수정일: 2026-02-05
"""

import sys
from pathlib import Path
from datetime import datetime

# 모듈 경로 추가
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from modules import connect_db, DB_HOST, DB_PORT, DB_NAME
from modules.calculate_trends import calculate_all_trends


def main():
    """배치 Job 메인 함수"""
    print("=" * 60)
    print("CALL:ACT Trend 계산 배치 Job")
    print("=" * 60)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print("=" * 60)

    # DB 연결
    conn = connect_db()

    try:
        # Trend 계산
        employee_count, inquiry_count = calculate_all_trends(conn)

        print("\n" + "=" * 60)
        print("[SUCCESS] 배치 Job 완료")
        print("=" * 60)
        print(f"  - 상담사 trend 업데이트: {employee_count}명")
        print(f"  - 자주 찾는 문의 trend 업데이트: {inquiry_count}건")
        print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n[ERROR] 배치 Job 실패: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
