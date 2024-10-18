import json
import subprocess
import sys
from datetime import datetime

# 관리자 계정 이름 변경 여부 확인 함수
def check_admin_account_name():
    try:
        result = subprocess.run(['powershell', '-Command', 'Get-LocalUser | Where-Object {$_.Name -eq "Administrator"}'],
                                capture_output=True, text=True, check=True)
        admin_account_exists = 'Administrator' in result.stdout
    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "Administrator 계정 정보를 가져오지 못했습니다."}

    if admin_account_exists:
        return {"status": "취약", "message": "Administrator 계정 이름이 변경되지 않았습니다."}
    else:
        return {"status": "양호", "message": "Administrator 계정 이름이 변경되었습니다."}

# 관리자 계정 이름 변경 함수
def remediate_admin_account():
    try:
        new_name = "SecureAdmin"  # 변경할 관리자 계정 이름
        result = subprocess.run(['powershell', '-Command', f'Rename-LocalUser -Name "Administrator" -NewName "{new_name}"'],
                                capture_output=True, text=True, check=True)
        return {"status": "완료", "message": f"Administrator 계정 이름을 {new_name}(으)로 변경했습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "Administrator 계정 이름 변경에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_admin_account()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_admin_account_name()

    # 조치 결과와 재진단 결과를 결합하여 최종 출력
    account_result = {
        "카테고리": "계정 관리",
        "항목 설명": "Administrator 계정 이름 변경 또는 보안성 강화",
        "중요도": "상",
        "진단 결과": "취약",  
        "조치 결과": remediation_result["status"], 
        "재진단 결과": diagnosis_result["status"], 
        "메시지": diagnosis_result["message"],
        "조치 파일명": "1.py",
        "조치 담당자": 담당자, 
        "조치 시각": remediation_date,
        "코드": "W-01"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
