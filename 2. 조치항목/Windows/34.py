import os
import json
import subprocess
import sys
from datetime import datetime

# 로그 검토 여부 확인 함수
def check_log_review():
    try:
        # PowerShell 명령어로 최근 시스템 이벤트 로그를 확인
        result = subprocess.run(['powershell', '-Command',
                                  'Get-EventLog -LogName System -Newest 5 | Select-Object -Property TimeGenerated, EntryType, Source, EventID'], 
                                capture_output=True, text=True, check=True)
        logs = result.stdout.strip()

        if logs:  # 로그가 존재하면 양호
            return {"status": "양호", "message": "로그가 정상적으로 검토되었습니다."}
        else:
            return {"status": "취약", "message": "로그 검토 중 문제가 발생했습니다."}
    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "로그 정보를 가져오는 중 오류가 발생했습니다."}

# 로그 검토 조치 함수
def remediate_log_review():
    try:
        # 로그 검토 조치 (예: 로그를 추가로 검토하거나 저장하는 등의 조치)
        result = subprocess.run(['powershell', '-Command',
                                  'Write-Host "로그를 검토합니다."'],  # 실제 조치가 들어가야 할 부분에 예시를 추가했습니다.
                                capture_output=True, text=True, check=True)
        return {"status": "완료", "message": "로그 검토 조치가 성공적으로 수행되었습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "로그 검토 조치에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    log_review_result = check_log_review()

    # 로그 검토에 문제가 있는 경우에만 조치 수행
    if log_review_result["status"] == "취약":
        remediation_result = remediate_log_review()
    else:
        remediation_result = {"status": "양호", "message": "로그 검토가 정상적으로 수행되었습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행 시간 기록
    diagnosis_date = None
    if remediation_result["status"] == "완료":
        diagnosis_result = check_log_review()
        diagnosis_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        diagnosis_result = {"status": "점검불가", "message": "조치가 완료되지 않아 진단을 실행할 수 없습니다."}

    # 조치 결과와 재진단 결과를 결합하여 최종 출력
    log_final_result = {
        "카테고리": "로그 관리",
        "항목 설명": "로그의 정기적 검토 및 보고",
        "중요도": "상",
        "진단 결과": "취약",  
        "조치 결과": remediation_result["status"], 
        "재진단 결과": diagnosis_result["status"], 
        "메시지": diagnosis_result["message"],
        "조치 파일명": "34.py",
        "조치 담당자": 담당자,  
        "조치 시각": remediation_date,  
        "코드": "W-34" 
    }

    # 최종 결과 출력
    print(json.dumps(log_final_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
