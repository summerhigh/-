import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 최신 Sendmail 버전 정보 (예: 8.15.2)
LATEST_SENDMAIL_VERSION = "8.15.2"

# Sendmail 버전 점검 함수
def check_sendmail_version():
    try:
        # Sendmail 버전 확인 명령어 실행
        sendmail_version_check = subprocess.run(['sendmail', '-d0.1'], capture_output=True, text=True, stderr=subprocess.STDOUT)
        
        if sendmail_version_check.returncode == 0:
            # 버전 정보 출력에서 Sendmail 버전 추출
            output = sendmail_version_check.stdout
            version_line = [line for line in output.splitlines() if "Version" in line]
            
            if version_line:
                current_version = version_line[0].split()[2]  # Version 정보 추출
                
                # 최신 버전과 비교
                if current_version >= LATEST_SENDMAIL_VERSION:
                    return "양호"  # 최신 버전 사용 중인 경우
                else:
                    return "취약"  # 취약한 버전 사용 중인 경우
        else:
            return "취약"  # Sendmail이 설치되어 있지만 버전을 확인할 수 없는 경우
    except FileNotFoundError:
        return "양호"  # Sendmail이 설치되어 있지 않음 (서비스 미사용)
    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검불가 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # Sendmail 버전 점검
    status = check_sendmail_version()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "Sendmail 버전 점검",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "30.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-30"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
