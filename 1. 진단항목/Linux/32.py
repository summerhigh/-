import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Sendmail 실행 방지 설정 여부를 점검하는 함수
def check_sendmail_restrict_qrun():
    try:
        # Sendmail 설정 파일 경로 (기본적으로 /etc/mail/sendmail.cf에서 점검)
        sendmail_config_file = '/etc/mail/sendmail.cf'

        # Sendmail 설정 파일이 존재하는지 확인
        if os.path.exists(sendmail_config_file):
            with open(sendmail_config_file, 'r') as f:
                content = f.read()

                # restrictqrun 옵션이 설정되어 있는지 확인
                if 'restrictqrun' in content.lower():
                    return "양호"  # 일반 사용자의 q 옵션이 제한된 경우
                else:
                    return "취약"  # q 옵션 제한이 설정되지 않은 경우
        else:
            return "양호"  # Sendmail 설정 파일이 없는 경우(즉, SMTP 사용하지 않음)

    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검불가 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 일반 사용자의 Sendmail 실행 방지 설정 점검
    status = check_sendmail_restrict_qrun()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "일반 사용자의 Sendmail 실행 방지",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "32.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-32"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
