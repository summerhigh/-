import os
import sys
import json
from datetime import datetime
import pwd

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# /etc/hosts.equiv 및 $HOME/.rhosts 파일 점검 함수
def check_rhosts_hosts_equiv():
    files_to_check = ['/etc/hosts.equiv']  # 점검할 파일 목록

    # 각 사용자 홈 디렉토리 내 .rhosts 파일도 추가
    for user in pwd.getpwall():
        home_dir = user.pw_dir
        rhosts_file = os.path.join(home_dir, '.rhosts')
        files_to_check.append(rhosts_file)

    try:
        for file_to_check in files_to_check:
            if os.path.exists(file_to_check):
                # 파일의 소유자 확인 (root 또는 파일 소유자여야 함)
                file_stat = os.stat(file_to_check)
                if file_stat.st_uid != 0 and file_stat.st_uid != pwd.getpwnam(os.path.basename(file_to_check)).pw_uid:
                    return "취약"  # 소유자가 root 또는 해당 계정이 아닌 경우

                # 파일 권한 확인 (600 이하이어야 함)
                file_permissions = oct(file_stat.st_mode)[-3:]
                if file_permissions > '600':
                    return "취약"  # 권한이 600 이하가 아닌 경우

                # 파일 내용 확인 ('+' 설정이 없어야 함)
                with open(file_to_check, 'r') as f:
                    content = f.read()
                    if '+' in content:
                        return "취약"  # '+' 설정이 포함된 경우

        return "양호"  # 모든 파일이 적절히 설정된 경우
    except Exception as e:
        return "점검불가"  # 오류 발생 시 취약 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # /etc/hosts.equiv 및 $HOME/.rhosts 파일 점검
    status = check_rhosts_hosts_equiv()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "$HOME/.rhosts, hosts.equiv 사용 금지",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "17.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-17"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
