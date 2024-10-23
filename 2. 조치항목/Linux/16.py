import os
import sys
import subprocess
import json
from datetime import datetime

# 존재하지 않는 device 파일 제거 함수
def remediate_invalid_device_files():
    try:
        # /dev 디렉토리에서 major, minor number가 없는 파일 검색
        result = subprocess.run(
            ['find', '/dev', '-type', 'f', '!', '-type', 'b', '!', '-type', 'c', '-print'],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )

        invalid_device_files = result.stdout.splitlines()

        if invalid_device_files:
            # 발견된 존재하지 않는 device 파일을 삭제
            for file in invalid_device_files:
                # 파일 삭제
                subprocess.run(['rm', '-f', file], check=False)

            return "완료"

        return "완료"  # 제거할 파일이 없는 경우
    except Exception as e:
        return "미완료"

# 존재하지 않는 device 파일 점검 함수 (재진단)
def check_invalid_device_files():
    try:
        # /dev 디렉토리에서 major, minor number가 없는 파일 검색
        result = subprocess.run(
            ['find', '/dev', '-type', 'f', '!', '-type', 'b', '!', '-type', 'c', '-ls'],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )

        # 결과가 있으면 취약한 상태 (존재하지 않는 device 파일이 있음)
        if result.stdout.strip():  # 결과가 비어있지 않으면 취약
            return {"status": "취약", "message": "존재하지 않는 device 파일이 존재합니다."}

        return {"status": "양호", "message": "존재하지 않는 device 파일이 존재하지 않습니다."}

    except Exception as e:
        return {"status": "점검불가", "message": "존재하지 않는 device 파일을 점검하는 중 오류가 발생했습니다."}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_invalid_device_files()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_invalid_device_files()

    # 최종 출력
    account_result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "/dev 디렉토리의 존재하지 않는 device 파일 점검",
        "중요도": "상",
        "진단 결과": "취약",
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "16.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-16"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
