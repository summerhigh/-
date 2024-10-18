import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 계정 잠금 임계값 확인 함수 (서버에 따라 다르게 진단)
def check_account_lock_threshold():
    try:
        # 첫 번째 시도: /etc/security/faillock.conf에서 계정 잠금 임계값 확인 (리눅스)
        result = subprocess.run(['grep', '^\s*deny', '/etc/security/faillock.conf'], capture_output=True, text=True)
        lock_value = int(result.stdout.split('=')[-1].strip()) if result.stdout else None
        
        # 두 번째 시도: /etc/pam.d/system-auth에서 pam_faillock.so의 deny 설정 확인 (리눅스 대체 경로)
        if lock_value is None:
            result = subprocess.run(['grep', 'pam_faillock.so', '/etc/pam.d/system-auth'], capture_output=True, text=True)
            if 'deny=' in result.stdout:
                lock_value = int(result.stdout.split('deny=')[-1].split()[0].strip())
        
        # 세 번째 시도: /etc/default/login에서 RETRIES 확인 (솔라리스 기반)
        if lock_value is None:
            result = subprocess.run(['grep', 'RETRIES', '/etc/default/login'], capture_output=True, text=True)
            lock_value = int(result.stdout.split('=')[-1].strip()) if result.stdout else None
        
        # 네 번째 시도: /etc/security/user에서 loginretries 확인 (AIX 기반)
        if lock_value is None:
            result = subprocess.run(['grep', 'loginretries', '/etc/security/user'], capture_output=True, text=True)
            lock_value = int(result.stdout.split('=')[-1].strip()) if result.stdout else None
        
        # 다섯 번째 시도: /tcb/files/auth/system/default에서 RETRIES 확인 (HP-UX 기반)
        if lock_value is None:
            result = subprocess.run(['grep', 'RETRIES', '/tcb/files/auth/system/default'], capture_output=True, text=True)
            lock_value = int(result.stdout.split('=')[-1].strip()) if result.stdout else None

        # 계정 잠금 임계값 설정 확인
        if lock_value is not None and lock_value <= 10:
            return "양호"  # 10회 이하로 설정된 경우
        else:
            return "취약"  # 10회 초과로 설정된 경우 또는 설정이 없을 때
    except Exception as e:
        return "점검불가"  # 파일이나 명령어 오류 발생 시

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 계정 잠금 임계값 설정 점검
    status = check_account_lock_threshold()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "계정 관리",
        "항목 설명": "계정 잠금 임계값 설정",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": "3.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-03"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
