import json
import subprocess
import sys
from datetime import datetime

# '해독 가능한 암호화 사용' 정책 확인 함수
def check_reversible_encryption_policy():
    try:
        # PowerShell 명령어로 '해독 가능한 암호화 사용' 정책 확인
        result = subprocess.run(['powershell', '-Command', 
                                 'Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Lsa" | Select-Object -ExpandProperty "StoreClearTextPasswords"'],
                                capture_output=True, text=True, check=True)
        value = result.stdout.strip()

        # StoreClearTextPasswords 값 확인 (0: 사용 안 함, 1: 사용)
        if value.isdigit() and int(value) == 0:
            return {"status": "양호", "message": "해독 가능한 암호화 사용이 '사용 안 함'으로 설정되어 있습니다."}
        else:
            return {"status": "취약", "message": "해독 가능한 암호화 사용이 '사용'으로 설정되어 있습니다."}
    
    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "해독 가능한 암호화 정책 정보를 가져오는 중 오류가 발생했습니다."}

# '해독 가능한 암호화 사용' 정책 수정 함수
def remediate_reversible_encryption_policy():
    try:
        # PowerShell 명령어로 '해독 가능한 암호화 사용' 정책을 0으로 설정 (사용 안 함)
        result = subprocess.run(['powershell', '-Command', 
                                 'Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Lsa" -Name "StoreClearTextPasswords" -Value 0'],
                                capture_output=True, text=True, check=True)
        return {"status": "완료", "message": "해독 가능한 암호화 사용 정책을 '사용 안 함'으로 설정했습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "해독 가능한 암호화 사용 정책 설정에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    encryption_policy_result = check_reversible_encryption_policy()

    # 정책이 잘못 설정된 경우에만 조치 수행
    if encryption_policy_result["status"] == "취약":
        remediation_result = remediate_reversible_encryption_policy()
    else:
        remediation_result = {"status": "양호", "message": "해독 가능한 암호화 사용 정책이 적절하게 설정되어 있습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_reversible_encryption_policy()

    # 조치 결과와 재진단 결과를 결합하여 최종 출력 (런처에 맞는 형식)
    encryption_result = {
        "카테고리": "보안 설정",
        "항목 설명": "'해독 가능한 암호화 사용 여부 확인'",
        "중요도": "상",
        "진단 결과": "취약",  # 진단 결과는 취약으로 고정
        "조치 결과": remediation_result["status"],  # 조치 결과
        "재진단 결과": diagnosis_result["status"],  # 재진단 결과
        "메시지": diagnosis_result["message"],
        "조치 파일명": "4.py",
        "조치 담당자": 담당자,  # 전달받은 담당자
        "조치 시각": remediation_date,  # 조치 일자
        "코드": "W-04"  # 고정된 코드
    }

    # 최종 결과 출력
    print(json.dumps(encryption_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
