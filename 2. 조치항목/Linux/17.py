import os
import sys
import subprocess
import json
from datetime import datetime
import pwd

# /etc/hosts.equiv 및 $HOME/.rhosts 파일 조치 함수
def remediate_rhosts_hosts_equiv():
    files_to_check = ['/etc/hosts.equiv']  # 점검할 파일 목록

    # 각 사용자 홈 디렉토리 내 .rhosts 파일도 추가
    for user in pwd.getpwall():
        home_dir = user.pw_dir
        rhosts_file = os.path.join(home_dir, '.rhosts')
        files_to_check.append(rhosts_file)

    try:
        for file_to_check in files_to_check:
            if os.path.exists(file_to_check):
                # 파일 소유자를 root 또는 해당 계정으로 변경
                file_stat = os.stat(file_to_check)
                if file_stat.st_uid != 0 and file_stat.st_uid != pwd.getpwnam(os.path.basename(file_to_check)).pw_uid:
                    subprocess.run(['chown', 'root', file_to_check], check=False)

                # 파일 권한을 600으로 변경
                file_permissions = oct(file_stat.st_mode)[-3:]
                if file_permissions > '600':
                    subprocess.run(['chmod', '600', file_to_check], check=False)

                # 파일 내용에서 '+' 설정을 제거
                with open(file_to_check, 'r') as f:
                    content = f.readlines()
                with open(file_to_check, 'w') as f:
                    for line in content:
                        if '+' not in line:
                            f.write(line)

        return "완료"

    except Exception as e:
        return "미완료"

# /etc/hosts.equiv 및 $HOME/.rhosts 파일 점검 함수 (재진단)
def check_rhosts_hosts_equiv():
    files_to_check = ['/etc/hosts.equiv']

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
                    return {"status": "취약", "message": f"{file_to_check} 파일의 소유자가 root 또는 해당 계정이 아닙니다."}

                # 파일 권한 확인 (600 이하이어야 함)
                file_permissions = oct(file_stat.st_mode)[-3:]
                if file_permissions > '600':
                    return {"status": "취약", "message": f"{file_to_check} 파일의 권한이 600 이하가 아닙니다."}

                # 파일 내용 확인 ('+' 설정이 없어야 함)
                with open(file_to_check, 'r') as f:
                    content = f.read()
                    if '+' in content:
                        return {"status": "취약", "message": f"{file_to_check} 파일에 '+' 설정이 포함되어 있습니다."}

        return {"status": "양호", "message": "모든 파일이 적절히 설정되었습니다."}
    
    except Exception as e:
        return {"status": "점검불가", "message": "파일 점검 중 오류가 발생했습니다."}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_rhosts_hosts_equiv()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_rhosts_hosts_equiv()

    # 최종 출력
    account_result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "$HOME/.rhosts, hosts.equiv 사용 금지",
        "중요도": "상",
        "진단 결과": "취약",
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "17.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-17"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
