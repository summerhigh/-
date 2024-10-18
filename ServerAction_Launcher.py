import os
import sys
import subprocess
import json
import socket
import platform
from datetime import datetime

# 디렉토리 경로 초기화
base_dir = None
action_base_dir = None
result_base_dir = None
log_dir = None

# 로그 파일명 생성
def create_log_file_path(result_dir):
    # 조치결과 디렉토리명 추출
    dir_name = os.path.basename(result_dir)
    parts = dir_name.split('_')
    if len(parts) == 2:
        조치일자 = parts[0]
        체크번호 = parts[1]
        log_file_name = f"log_{조치일자}_{체크번호}.txt"
    else:
        log_file_name = "log_Unknown.txt"

    return os.path.join(log_dir, log_file_name)

# 로그 기록
def log_message(log_file_path, message):
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")
    print(message)

# 조치 실행
def run_action_script(script_path, json_output_path, 담당자, log_file_path):
    try:
        result = subprocess.run(['python', script_path, 담당자], capture_output=True, text=True, check=True)
        action_result = json.loads(result.stdout)

        with open(json_output_path, 'w', encoding='utf-8') as json_file:
            json.dump(action_result, json_file, ensure_ascii=False, indent=4)

        log_message(log_file_path, f"조치 성공: {script_path}")
        return action_result
    except Exception as e:
        log_message(log_file_path, f"조치 실패: {script_path} - 오류: {str(e)}")
        return None

# 조치할 진단결과 선택
def get_vulnerable_items(directories):
    print(f"현재 시스템은 {socket.gethostname()}입니다.\n조치할 진단 디렉토리를 선택하세요.")
    
    # 디렉토리 경로의 마지막 두 폴더명만 출력
    for idx, directory in enumerate(directories):
        # 상위 디렉토리명과 마지막 디렉토리명 추출
        parent_dir = os.path.basename(os.path.dirname(directory))
        base_dir = os.path.basename(directory)
        print(f"{idx+1}. {parent_dir}\\{base_dir}")

    choice = input("번호를 입력하세요: ").strip()
    
    if not choice.isdigit() or int(choice) not in range(1, len(directories) + 1):
        print("잘못된 입력입니다. 다시 시도하세요.")
        return get_vulnerable_items(directories)

    return directories[int(choice) - 1]

# 시스템 이름이 일치하는 디렉토리 찾기
def find_matching_directories(base_path, system_name):
    matching_dirs = []
    for root, dirs, files in os.walk(base_path):
        if 'info.json' in files:
            with open(os.path.join(root, 'info.json'), 'r', encoding='utf-8') as f:
                info = json.load(f)
                # 시스템 목록에서 시스템 이름을 찾아 확인
                for system in info.get('시스템 목록', []):
                    if system.get('시스템 이름') == system_name:
                        matching_dirs.append(root)
                        break
    return matching_dirs

# 취약 항목리스트 출력
def show_vulnerabilities(vulnerable_items):
    for idx, item in enumerate(vulnerable_items, 1):
        print(f"{idx}. {item['code']} - {item['description']}")

# 조치 실행 항목 출력
def process_vulnerable_items(vulnerable_items, system_os, 담당자, check_dir, log_file_path):
    for item in vulnerable_items:
        script_file = f"{item['code']}.py"
        script_path = os.path.join(base_dir, system_os, script_file)

        if os.path.exists(script_path):
            result_file = os.path.join(check_dir, f"{item['code']}.json")
            run_action_script(script_path, result_file, 담당자, log_file_path)

# 메인 메소드
def main():
    # 전역 변수 설정
    global base_dir, action_base_dir, result_base_dir, log_dir

    # 현재 시스템명, 운영체제 확인
    system_name = socket.gethostname()
    current_os = platform.system()

    # 현재 프로그램이 위치한 디렉토리 경로
    current_dir = os.path.dirname(__file__)

    # 운영체제에 따른 파일 경로 설정
    if current_os == "Windows":
        base_dir = os.path.join(current_dir, "3. 진단결과", "Windows")
        action_base_dir = os.path.join(current_dir, "2. 조치항목", "Windows")
        result_base_dir = os.path.join(current_dir, "4. 조치결과", "Windows")
    elif current_os == "Linux":
        base_dir = os.path.join(current_dir, "3. 진단결과", "Linux")
        action_base_dir = os.path.join(current_dir, "2. 조치항목", "Linux")
        result_base_dir = os.path.join(current_dir, "4. 조치결과", "Linux")
    else:
        sys.exit(f"지원되지 않는 운영체제입니다: {current_os}. \n프로그램 종료합니다.")

    # 로그 디렉토리 설정
    log_dir = os.path.join(result_base_dir, "Log")

    # 담당자 이름 입력
    담당자 = input("조치 담당자의 이름을 입력하세요: ").strip()

    # 시스템 이름이 일치하는 진단 디렉토리를 찾기
    matching_dirs = find_matching_directories(base_dir, system_name)

    if not matching_dirs:
        print(f"해당 시스템({system_name})에 대한 진단 디렉토리가 없습니다. \n진단을 먼저 수헹헤주세요.")
        return

    # 조치할 디렉토리 선택
    chosen_dir = get_vulnerable_items(matching_dirs)

    # 취약 항목 추출
    vulnerable_items = []
    for root, dirs, files in os.walk(chosen_dir):
        for file in files:
            if file.endswith('.json') and file.isdigit():
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for code, details in data.get('진단 항목', {}).items():
                        if details.get('진단 결과') == '취약':
                            vulnerable_items.append({
                                'code': code,
                                'description': details['항목 설명']
                            })

    if not vulnerable_items:
        print("취약 항목이 없습니다.")
        return

    # 취약 항목 리스트 출력 및 조치 진행 여부 확인
    show_vulnerabilities(vulnerable_items)
    should_proceed = input("이 항목들을 조치할까요? (y/n): ").strip().lower()

    if should_proceed == 'y' or should_proceed == '':
        # 조치 디렉토리 생성
        today = datetime.now().strftime("%Y%m%d")
        check_dir = os.path.join(result_base_dir, f"{today}_check{matching_dirs.index(chosen_dir)+1}")
        os.makedirs(check_dir, exist_ok=True)

        # 로그 파일명, 경로 지정
        log_file_path = create_log_file_path(check_dir)

        # 취약 항목 조치 실행
        process_vulnerable_items(vulnerable_items, current_os, 담당자, check_dir, log_file_path)

        print("모든 조치가 완료되었습니다.")
    else:
        print("조치가 취소되었습니다.")

if __name__ == "__main__":
    main()