import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# SMTP 릴레이 제한 설정 여부를 점검하는 함수
def check_smtp_relay_restriction():
    try:
        # Sendmail 설정 파일 경로 (기본적으로 /etc/mail/sendmail.cf에서 점검)
        sendmail_config_file = '/etc/mail/sendmail.cf'

        # Sendmail 설정 파일이 존재하는지 확인
        if os.path.exists(sendmail_config_file):
            with open(sendmail_config_file, 'r') as f:
                content = f.read()

                # SMTP 릴레이 제한 설정 확인 (Relay 사용 여부, 허가되지 않은 접근 제어 설정)
                if 'relay_mail_from' in content.lower() or 'authinfo' in content.lower():
                    return "양호"  # 릴레이 제한이 설정된 경우
                else:
                    return "취약"  # 릴레이 제한이 설정되지 않은 경우
        else:
            return "양호"  # Sendmail 설정 파일이 없는 경우(즉, SMTP 사용하지 않음)

    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검불가 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # SMTP 릴레이 제한 설정 점검
    status = check_smtp_relay_restriction()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "SMTP 릴레이 제한",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "31.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-31"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
