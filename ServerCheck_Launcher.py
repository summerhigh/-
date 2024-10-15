import os
import subprocess
import json
import socket
import platform
import sys 
import platform
from datetime import datetime
from make_json import make_json # json 통합 프로그램 모듈화

# 운영체제에 맞는 base_dir을 설정하기 위한 변수 초기화
base_dir = None
result_base_dir = None
log_dir = None

# 로그 파일명 생성 함수
def create_log_file_path(result_dir):
    dir_name = os.path.basename(result_dir)
    parts = dir_name.split('_')
    if len(parts) == 2:
        진단일자 = parts[0]
        체크번호 = parts[1]
        log_file_name = f"log_{진단일자}_{체크번호}.txt"
    else:
        log_file_name = "log_Unknown.txt"

    return os.path.join(log_dir, log_file_name)

# 로그 기록 함수
def log_message(log_file_path, message):
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")
    print(message)

# 진단 파일 실행 함수
def run_diagnosis_script(script_path, json_output_path, 담당자, log_file_path):
    try:
        result = subprocess.run(['python', script_path, 담당자], capture_output=True, text=True, check=True)
        diagnosis_result = json.loads(result.stdout)

        with open(json_output_path, 'w', encoding='utf-8') as json_file:
            json.dump(diagnosis_result, json_file, ensure_ascii=False, indent=4)

        log_message(log_file_path, f"진단 성공: {script_path}")
        return diagnosis_result
    except Exception as e:
        log_message(log_file_path, f"진단 실패: {script_path} - 오류: {str(e)}")
        return None

# 사용자 입력 받기
def get_diagnosis_range():
    print("진단 방식을 선택하세요. 1. 전체 2. 부분")
    선택 = input("입력: ").strip()

    if 선택 == '1':
        return "전체", []
    elif 선택 == '2':
        범위 = input("1~37 항목에서 진단할 범위를 설정해주세요. (예시: 1,2,5-10): ").strip()
        범위_리스트 = parse_range(범위)
        return "부분", 범위_리스트
    else:
        print("잘못된 입력입니다. 다시 시도하세요.")
        return get_diagnosis_range()

# 범위 파싱 함수 (예: '1,2,5-10'을 리스트로 변환)
def parse_range(range_str):
    result = []
    ranges = range_str.split(',')
    for r in ranges:
        if '-' in r:
            start, end = map(int, r.split('-'))
            result.extend(range(start, end + 1))
        else:
            result.append(int(r))
    return result

def check_files_exist(file_numbers):
    global base_dir  # 전역 변수 사용
    while True:
        existing_files = []
        missing_files = []

        # base_dir에 진단 파일들이 제대로 있는지 확인
        for num in file_numbers:
            file_path = os.path.join(base_dir, f"{num}.py")
            # 디버깅용: 경로 확인
            print(f"확인 중인 파일 경로: {file_path}")
            if os.path.exists(file_path):
                existing_files.append(num)
            else:
                missing_files.append(num)

        # 모든 항목이 존재하지 않을 경우 다시 선택하도록 처리
        if len(existing_files) == 0:
            print("선택한 모든 항목이 존재하지 않습니다. 잘못된 입력입니다. 다시 시도하세요.")
            진단_방식, file_numbers = get_diagnosis_range()  # 새 항목을 선택하게 하는 함수
            continue  # 루프 다시 시작

        # 일부 파일이 존재하지 않을 때 사용자에게 진단을 계속할지 물어봄
        if missing_files:
            print(f"항목 {', '.join(map(str, missing_files))}가 없습니다.")
            응답 = input(f"항목 {', '.join(map(str, existing_files))}을(를) 진단하시겠습니까? (y/n): ").strip().lower()
            if 응답 == 'y':
                return existing_files
            else:
                return []

        # 모든 항목이 유효할 경우 리스트 반환
        return existing_files

# 디렉토리 이름 생성 함수
def create_unique_directory_name(base_dir):
    timestamp = datetime.now().strftime("%Y%m%d")
    check_number = 1
    dir_name = f"{timestamp}_check{check_number}"
    result_dir = os.path.join(base_dir, dir_name)

    while os.path.exists(result_dir):
        check_number += 1
        dir_name = f"{timestamp}_check{check_number}"
        result_dir = os.path.join(base_dir, dir_name)
    
    os.makedirs(result_dir)
    return result_dir

# info.json 생성 메소드
def generate_info_json(result_dir, log_file_path):
    system_info = {
        "시설명": "주요정보통신기반시설1",
        "진단 시작일자": "",
        "진단 종료일자": "",
        "시스템 목록": [
            {
                "시스템 이름": socket.gethostname(),
                "IP 주소": socket.gethostbyname(socket.gethostname()),
                "운영 체제": platform.system(), 
                "운영 체제 버전": platform.version(),
                "지역": "서울"
            }
        ]
    }

    info_json_path = os.path.join(result_dir, "info.json")
    with open(info_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(system_info, json_file, ensure_ascii=False, indent=4)

    log_message(log_file_path, f"info.json 생성 완료: {info_json_path}")
    return info_json_path

# 메인 실행 함수
def main():
    global base_dir, result_base_dir, log_dir  # 전역 변수 설정
    # 현재 운영체제 판별
    current_os = platform.system()

    # 운영체제에 따른 파일 경로 설정
    if current_os == "Windows":
        base_dir = os.path.join(os.path.dirname(__file__), "1. 진단항목", "Windows")
        result_base_dir = os.path.join(os.path.dirname(__file__), "3. 진단결과", "Windows")
    elif current_os == "Linux":
        base_dir = os.path.join(os.path.dirname(__file__), "1. 진단항목", "Linux")
        result_base_dir = os.path.join(os.path.dirname(__file__), "3. 진단결과", "Linux")
    else:
        sys.exit(f"지원되지 않는 운영체제입니다: {current_os}. 프로그램을 종료합니다.")

    log_dir = os.path.join(result_base_dir, "Log")

    # 운영체제에 따라 사용자에게 질문
    while True:
        if current_os == "Windows":
            응답 = input("현재 운영체제는 Windows입니다. 진단하시겠습니까? (y/n): ").strip().lower()
        elif current_os == "Linux":
            응답 = input("현재 운영체제는 Linux입니다. 진단하시겠습니까? (y/n): ").strip().lower()
        else:
            print(f"현재 운영체제는 {current_os}입니다. 지원되지 않는 운영체제일 수 있습니다.")
            sys.exit("지원되지 않는 운영체제입니다. 프로그램을 종료합니다.") 

        # 올바른 입력인지 확인
        if 응답 in ['y', 'n', '']:
            break
        else:
            print("잘못된 입력입니다. 다시 시도하세요.")

    # 'n'을 선택한 경우 프로그램 종료
    if 응답 == 'n':
        sys.exit("진단 프로그램을 종료합니다.") 

    # 진단 담당자 이름 입력
    진단자 = input("진단 담당자의 이름을 입력하세요: ").strip()

    # 진단 방식 및 범위 선택
    진단_방식, 진단_범위 = get_diagnosis_range()

    if 진단_방식 == "전체":
        진단_범위 = list(range(1, 38))  # range를 리스트로 변환하여 일관성 유지

    # 진단할 파일 확인
    valid_files = check_files_exist(진단_범위)

    if not valid_files:
        print("유효한 진단 파일이 없습니다.")
        return

    # 결과 디렉터리 생성
    result_dir = create_unique_directory_name(result_base_dir)

    # 로그 파일 경로 생성
    log_file_path = create_log_file_path(result_dir)

    # 로그 디렉터리가 없을 경우 생성
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # info.json 파일 생성
    generate_info_json(result_dir, log_file_path)

    # 진단 스크립트 실행 및 결과 저장
    for file_num in valid_files:
        script_path = os.path.join(base_dir, f"{file_num}.py")
        json_output_path = os.path.join(result_dir, f"{file_num}.json")
        run_diagnosis_script(script_path, json_output_path, 진단자, log_file_path)

    # 통합 JSON 파일 생성 여부 묻기
    while True:
        통합_응답 = input("통합 JSON 파일을 생성하시겠습니까? (y/n): ").strip().lower()

        # 올바른 입력인지 확인
        if 통합_응답 in ['y', 'n', '']:
            break
        else:
            print("잘못된 입력입니다. 다시 시도하세요.")

    # 통합을 원하는 경우만 JSON 파일 생성
    if 통합_응답 == 'y':
        make_json(result_dir, log_file_path, log_message)
        log_message(log_file_path, f"진단 완료. \n결과는 {result_dir}에 저장되었습니다.")
    else:
        log_message(log_file_path, f"통합 JSON 파일 생성을 건너뜁니다. \n진단 완료. \n결과는 {result_dir}에 저장되었습니다.")

if __name__ == "__main__":
    main()