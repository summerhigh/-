import os
import sys
import subprocess
import json
from datetime import datetime

# 소유자가 없는 파일 및 디렉터리 삭제 또는 소유자 변경 조치 함수
def remediate_orphaned_files():
    try:
        # 첫 번째 시도: 리눅스 및 대부분의 유닉스에서 소유자가 없는 파일 및 디렉터리 삭제 또는 소유자 변경
        result = subprocess.run(['find', '/home', '/var', '/etc', '-nouser', '-o', '-nogroup'], capture_output=True, text=True)

        orphaned_files = result.stdout.splitlines()

        if orphaned_files:
            # 불필요한 파일은 삭제하고, 필요한 경우 소유자 변경
            for file in orphaned_files:
                # 예시: 삭제가 필요한 파일은 삭제 (rm 명령어 사용)
                subprocess.run(['rm', '-f', file], check=False)

                # 예시: 소유자를 변경해야 하는 파일은 소유자 변경 (chown 명령어 사용)
                # subprocess.run(['chown', 'new_owner', file], check=False)

            return "완료"

        # 두 번째 시도: AIX에서 소유자가 없는 파일을 찾기 위한 대체 명령어
        result = subprocess.run(['find', '/home', '/var', '/etc', '-fstype', 'jfs2', '-nouser', '-o', '-nogroup'], capture_output=True, text=True)
        orphaned_files = result.stdout.splitlines()

        if orphaned_files:
            for file in orphaned_files:
                subprocess.run(['rm', '-f', file], check=False)
            return "완료"

        # 세 번째 시도: HP-UX에서 소유자가 없는 파일을 찾기 위한 대체 명령어
        result = subprocess.run(['find', '/home', '/var', '/etc', '-fstype', 'hfs', '-nouser', '-o', '-nogroup'], capture_output=True, text=True)
        orphaned_files = result.stdout.splitlines()

        if orphaned_files:
            for file in orphaned_files:
                subprocess.run(['rm', '-f', file], check=False)
            return "완료"

        return "완료"  # 소유자가 없는 파일이 없는 경우 완료로 처리
    except Exception as e:
        return "미완료"

# 소유자가 없는 파일 및 디렉터리 확인 함수 (재진단)
def check_orphaned_files():
    try:
        # 첫 번째 시도: 리눅스 및 대부분의 유닉스에서 소유자가 없는 파일 및 디렉터리 확인
        result = subprocess.run(['find', '/home', '/var', '/etc', '-nouser', '-o', '-nogroup'], capture_output=True, text=True)

        # 두 번째 시도: AIX에서 소유자가 없는 파일을 찾기 위한 대체 명령어
        if result.returncode != 0 or not result.stdout:
            result = subprocess.run(['find', '/home', '/var', '/etc', '-fstype', 'jfs2', '-nouser', '-o', '-nogroup'], capture_output=True, text=True)

        # 세 번째 시도: HP-UX에서 소유자가 없는 파일을 찾기 위한 대체 명령어
        if result.returncode != 0 or not result.stdout:
            result = subprocess.run(['find', '/home', '/var', '/etc', '-fstype', 'hfs', '-nouser', '-o', '-nogroup'], capture_output=True, text=True)

        # 명령어 실행 결과 확인
        if result.returncode == 0 and result.stdout:
            return {"status": "취약", "message": "소유자가 없는 파일 및 디렉터리가 존재합니다."}
        else:
            return {"status": "양호", "message": "소유자가 없는 파일 및 디렉터리가 없습니다."}
    except Exception as e:
        return {"status": "점검불가", "message": "소유자가 없는 파일 및 디렉터리를 확인할 수 없습니다."}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_orphaned_files()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_orphaned_files()

    # 최종 출력
    account_result = {
        "카테고리": "파일 및 디렉터리 관리",
        "항목 설명": "파일 및 디렉터리 소유자 설정",
        "중요도": "상",
        "진단 결과": "취약",
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "6.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-06"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
