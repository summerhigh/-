import os
import sys
import subprocess
import json
from datetime import datetime

# world writable 파일 제거 함수
def remediate_world_writable_files():
    try:
        # world writable 파일을 찾기 위한 명령어 실행
        result = subprocess.run(
            ['find', '/', '-xdev', '-type', 'f', '-perm', '-0002', '-print'],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )

        world_writable_files = result.stdout.splitlines()

        if world_writable_files:
            # 발견된 world writable 파일에서 쓰기 권한 제거 또는 파일 삭제
            for file in world_writable_files:
                # 쓰기 권한 제거
                subprocess.run(['chmod', 'o-w', file], check=False)
                # 필요 시 파일 삭제 예시:
                # subprocess.run(['rm', '-rf', file], check=False)

            return "완료"

        return "완료"  # world writable 파일이 없는 경우 완료로 처리
    except Exception as e:
        return "미완료"

# world writable 파일 점검 함수 (재진단)
def check_world_writable_files():
    try:
        # world writable 파일을 찾기 위한 명령어 실행
        result = subprocess.run(
            ['find', '/', '-xdev', '-type', 'f', '-perm', '-0002', '-ls'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # 예외: 명령어 실행 후 반환 코드가 0이 아닐 경우 오류 처리
        if result.returncode != 0:
            return {"status": "점검불가", "message": "world writable 파일을 확인하는 중 오류가 발생했습니다."}

        # 결과가 있으면 취약한 상태 (world writable 파일이 존재)
        if result.stdout.strip():  # 결과가 비어있지 않으면 취약
            return {"status": "취약", "message": "world writable 파일이 존재합니다."}

        return {"status": "양호", "message": "world writable 파일이 존재하지 않습니다."}
    except Exception as e:
        return {"status": "점검불가", "message": "world writable 파일을 확인하는 중 오류가 발생했습니다."}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_world_writable_files()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_world_writable_files()

    # 최종 출력
    account_result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "World Writable 파일 점검",
        "중요도": "상",
        "진단 결과": "취약",
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "15.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-15"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
