import json
import subprocess
import sys
from datetime import datetime

# 계정 잠금 임계값 확인 함수
def check_account_lockout_threshold():
    try:
        # 'net accounts' 명령어로 계정 잠금 임계값 확인
        result = subprocess.run(['net', 'accounts'], capture_output=True, text=True, check=True)
        output = result.stdout.lower()

        # '잠금 임계값' 또는 'lockout threshold' 값을 찾기 위한 문자열 검색
        threshold_value = None
        for line in output.splitlines():
            if '잠금 임계값' in line or 'lockout threshold' in line:
                threshold_value = int(line.split()[-1])  # 마지막 값이 임계값 숫자임
                break

        if threshold_value is None:
            return {"status": "점검불가", "message": "계정 잠금 임계값 정보를 가져오지 못했습니다."}

        # 잠금 임계값 판단 기준
        if threshold_value <= 5:
            return {"status": "양호", "message": f"계정 잠금 임계값이 {threshold_value}(으)로 설정되어 있습니다."}
        else:
            return {"status": "취약", "message": f"계정 잠금 임계값이 {threshold_value}(으)로 설정되어 있습니다."}
    
    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "계정 잠금 임계값 정보를 가져오는 중 오류가 발생했습니다."}

# 계정 잠금 임계값 수정 함수
def remediate_account_lockout_threshold():
    try:
        # 'net accounts' 명령어로 계정 잠금 임계값을 5로 설정
        result = subprocess.run(['net', 'accounts', '/lockoutthreshold:5'], capture_output=True, text=True, check=True)
        return {"status": "완료", "message": "계정 잠금 임계값을 5로 설정했습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "계정 잠금 임계값 설정에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    lockout_threshold_result = check_account_lockout_threshold()

    # 임계값이 잘못 설정된 경우에만 조치 수행
    if lockout_threshold_result["status"] == "취약":
        remediation_result = remediate_account_lockout_threshold()
    else:
        remediation_result = {"status": "양호", "message": "계정 잠금 임계값이 적절하게 설정되어 있습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_account_lockout_threshold()

    # 조치 결과와 재진단 결과를 결합하여 최종 출력
    lockout_result = {
        "카테고리": "계정 관리",
        "항목 설명": "계정 잠금 임계값 설정",
        "중요도": "상",
        "진단 결과": "취약",  
        "조치 결과": remediation_result["status"], 
        "재진단 결과": diagnosis_result["status"], 
        "메시지": diagnosis_result["message"],
        "조치 파일명": "5.py",
        "조치 담당자": 담당자, 
        "조치 시각": remediation_date, 
        "코드": "W-05"  
    }

    # 최종 결과 출력
    print(json.dumps(lockout_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
