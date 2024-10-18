import os
import json
import subprocess
import sys
from datetime import datetime

# SAM 파일 접근 권한 설정 여부 확인 함수
def check_sam_permissions():
    try:
        # icacls 명령어로 SAM 파일 권한 확인
        result = subprocess.run(['icacls', 'C:\\Windows\\System32\\config\\SAM'], 
                                capture_output=True, text=True)
        output = result.stdout.lower()

        # 'administrator'와 'system'만 포함되어 있는지 확인
        # 'everyone'이나 기타 그룹이 포함되지 않은 경우 양호로 간주
        if 'nt authority\\system' in output and 'builtin\\administrators' in output and 'everyone' not in output:
            return {"status": "양호", "message": "SAM 파일의 접근 권한이 적절하게 설정되어 있습니다."}
        else:
            return {"status": "취약", "message": "SAM 파일의 접근 권한에 취약점이 있습니다."}
    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "SAM 파일 접근 권한 정보를 가져오는 중 오류가 발생했습니다."}

# SAM 파일 접근 권한 조치 함수
def remediate_sam_permissions():
    try:
        # icacls 명령어로 SAM 파일에서 불필요한 권한 제거
        result = subprocess.run(['icacls', 'C:\\Windows\\System32\\config\\SAM', '/remove', 'Everyone'], 
                                capture_output=True, text=True, check=True)
        return {"status": "완료", "message": "SAM 파일의 접근 권한을 성공적으로 수정했습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "SAM 파일의 접근 권한 수정에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    sam_permissions_result = check_sam_permissions()

    # SAM 파일 권한에 문제가 있는 경우에만 조치 수행
    if sam_permissions_result["status"] == "취약":
        remediation_result = remediate_sam_permissions()
    else:
        remediation_result = {"status": "양호", "message": "SAM 파일의 접근 권한이 이미 적절하게 설정되어 있습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행 시간 기록
    diagnosis_date = None
    if remediation_result["status"] == "완료" or remediation_result["status"] == "부분완료":
        diagnosis_result = check_sam_permissions()
        diagnosis_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        diagnosis_result = {"status": "점검불가", "message": "조치가 완료되지 않아 진단을 실행할 수 없습니다."}

    # 조치 결과와 진단 결과를 결합하여 최종 출력
    sam_final_result = {
        "카테고리": "보안 관리",
        "항목 설명": "SAM 파일 접근 통제 설정",
        "중요도": "상",
        "진단 결과": sam_permissions_result["status"],  
        "조치 결과": remediation_result["status"], 
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "sam_permissions.py",
        "조치 담당자": 담당자, 
        "조치 시각": remediation_date,  
        "코드": "W-37" 
    }

    # 최종 결과 출력
    print(json.dumps(sam_final_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
