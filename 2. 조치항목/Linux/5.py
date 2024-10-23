import os
import sys
import subprocess
import json
from datetime import datetime

# root 계정의 PATH 환경변수에서 "."을 마지막으로 이동하는 조치 함수
def remediate_root_path_variable():
    try:
        # 첫 번째 시도: /etc/profile 파일 수정 (리눅스/솔라리스/AIX/HP-UX)
        profile_path = '/etc/profile'
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as file:
                lines = file.readlines()

            # PATH 환경변수에서 "."을 마지막으로 이동
            with open(profile_path, 'w') as file:
                for line in lines:
                    if line.startswith('PATH='):
                        line = line.replace('PATH=.:', 'PATH=').replace(':.:', ':')
                        file.write(line.strip() + ':.\n')
                    else:
                        file.write(line)

            return "완료"

        # 두 번째 시도: root 계정의 .profile 파일 수정 (홈 디렉터리 환경설정)
        root_profile_path = '/root/.profile'
        if os.path.exists(root_profile_path):
            with open(root_profile_path, 'r') as file:
                lines = file.readlines()

            # PATH 환경변수에서 "."을 마지막으로 이동
            with open(root_profile_path, 'w') as file:
                for line in lines:
                    if line.startswith('PATH='):
                        line = line.replace('PATH=.:', 'PATH=').replace(':.:', ':')
                        file.write(line.strip() + ':.\n')
                    else:
                        file.write(line)

            return "완료"

        return "완료"  # 파일이 없는 경우 완료로 처리 (서비스 사용 안함)
    except Exception as e:
        return "미완료"

# root 계정의 PATH 환경변수에서 "." 위치 재확인 함수 (재진단)
def check_root_path_variable():
    try:
        # 첫 번째 시도: os.environ에서 root 계정의 PATH 환경변수 가져오기
        root_path = os.environ.get('PATH')

        if not root_path:
            # 두 번째 시도: 유닉스 시스템에서 `echo $PATH` 명령어로 PATH 환경변수 확인
            result = subprocess.run(['echo', '$PATH'], capture_output=True, text=True)
            root_path = result.stdout.strip()

        if not root_path:
            return {"status": "점검불가", "message": "PATH 환경변수를 확인할 수 없습니다."}

        # PATH를 콜론(:)으로 구분하여 리스트로 변환
        path_elements = root_path.split(':')

        # PATH의 각 요소를 확인하여 "."이 맨 앞이나 중간에 있는지 점검
        if '.' in path_elements and path_elements.index('.') != len(path_elements) - 1:
            return {"status": "취약", "message": "PATH 환경변수에 '.'이 맨 앞이나 중간에 있습니다."}
        else:
            return {"status": "양호", "message": "PATH 환경변수에 '.'이 없습니다 또는 마지막에만 있습니다."}

    except Exception as e:
        return {"status": "점검불가", "message": "PATH 환경변수 확인 중 오류가 발생했습니다."}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_root_path_variable()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_root_path_variable()

    # 최종 출력
    account_result = {
        "카테고리": "파일 및 디렉터리 관리",
        "항목 설명": "root홈, 패스 디렉터리 권한 및 패스 설정",
        "중요도": "상",
        "진단 결과": "취약", 
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "5.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-05"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()