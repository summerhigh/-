import os
import sys
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# crond 파일 소유자 및 권한 설정 점검 함수
def check_cron_permissions():
    try:
        # 점검할 cron 관련 파일 목록
        cron_files = ['/etc/cron.allow', '/etc/cron.deny', '/etc/crontab', '/var/spool/cron', '/etc/cron.d']

        for file in cron_files:
            if os.path.exists(file):
                # 파일 소유자가 root(0)인지 확인
                file_stat = os.stat(file)
                if file_stat.st_uid != 0:
                    return "취약"  # 소유자가 root가 아닌 경우

                # 파일 권한이 640 이하인지 확인
                file_permissions = oct(file_stat.st_mode)[-3:]
                if file_permissions > '640':
                    return "취약"  # 권한이 640 이상인 경우

        # cron.allow 파일이 있으면, 사용 가능한 사용자 확인
        if os.path.exists('/etc/cron.allow'):
            with open('/etc/cron.allow', 'r') as f:
                if f.read().strip():  # cron.allow 파일에 사용자가 정의되어 있으면 취약
                    return "취약"

        # cron.deny 파일이 있으면, deny 파일이 정의되어 있지 않으면 취약
        if os.path.exists('/etc/cron.deny'):
            with open('/etc/cron.deny', 'r') as f:
                if not f.read().strip():  # cron.deny 파일에 사용자가 없으면 취약
                    return "취약"

        return "양호"  # 모든 설정이 적절한 경우
    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검불가로 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # crond 파일 소유자 및 권한 점검
    status = check_cron_permissions()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "crond 파일 소유자 및 권한 설정",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "22.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-22"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
