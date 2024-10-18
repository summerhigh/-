import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Anonymous FTP 비활성화 여부를 점검하는 함수
def check_anonymous_ftp():
    try:
        # vsftpd.conf 또는 ftp 서버 설정 파일에서 Anonymous FTP 설정 확인
        ftp_config_files = ['/etc/vsftpd.conf', '/etc/ftpaccess', '/etc/proftpd/proftpd.conf']
        anonymous_ftp_enabled = False

        for config_file in ftp_config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    content = f.read().lower()
                    if 'anonymous_enable=YES'.lower() in content or 'anonftp' in content or 'guest_enable=YES'.lower() in content:
                        anonymous_ftp_enabled = True
                        break

        # FTP 데몬이 실행 중이고, 익명 접속이 활성화된 경우
        if anonymous_ftp_enabled:
            return "취약"  # Anonymous FTP가 활성화된 경우
        else:
            return "양호"  # Anonymous FTP가 비활성화된 경우

    except Exception as e:
        return "점검불가"  # 오류 발생 시 취약 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # Anonymous FTP 비활성화 여부 점검
    status = check_anonymous_ftp()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "Anonymous FTP 비활성화",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "20.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-20"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))