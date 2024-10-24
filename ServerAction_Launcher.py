import os
import subprocess
import json
import socket
import platform
from datetime import datetime

# 운영체제 확인 및 경로 및 명령어 설정
current_os = platform.system()

# 현재 스크립트의 위치를 기준으로 경로 설정
base_dir = os.path.dirname(__file__)

# 운영체제에 따른 경로 및 Python 명령어 설정
if current_os == "Linux":
    result_base_dir = os.path.join(base_dir, "3. 진단결과", "Linux")
    action_base_dir = os.path.join(base_dir, "4. 조치결과", "Linux")
    fix_script_base_dir = os.path.join(base_dir, "2. 조치항목", "Linux")
    log_dir = os.path.join(base_dir, "4. 조치결과", "Linux", "Log")
    python_cmd = "python3"
else:
    result_base_dir = os.path.join(base_dir, "3. 진단결과", "Windows")
    action_base_dir = os.path.join(base_dir, "4. 조치결과", "Windows")
    fix_script_base_dir = os.path.join(base_dir, "2. 조치항목", "Windows")
    log_dir = os.path.join(base_dir, "4. 조치결과", "Windows", "Log")
    python_cmd = "python"

# HWID 가져오는 함수
def get_hwid():
    try:
        if platform.system() == "Windows":
            # wmic 명령어 실행 (Windows)
            gethwid = subprocess.run(
                ["wmic", "diskdrive", "get", "serialnumber"],
                capture_output=True,
                text=True
            )
            
            output_lines = gethwid.stdout.strip().splitlines()

            # 빈 라인과 불필요한 공백 제거
            output_lines = [line.strip() for line in output_lines if line.strip()]

            if len(output_lines) > 1:
                hwid = output_lines[1].strip().rstrip(".")  # 끝의 . 제거
                return hwid
            else:
                return "Unknown-HWID"

        elif platform.system() == "Linux":
            # Linux에서 product_uuid 가져오기 (root 권한 필요)
            gethwid = subprocess.run(
                ["sudo", "cat", "/sys/class/dmi/id/product_uuid"],
                capture_output=True,
                text=True
            )
            
            if gethwid.returncode == 0:
                hwid = gethwid.stdout.strip()
                return hwid
            else:
                return "Unknown-HWID"

    except Exception as e:
        print(f"HWID를 가져오는 중 오류 발생: {str(e)}")
        return "Unknown-HWID"
    
# 로그 파일명 생성
def create_log_file_path(result_dir):
    # 진단결과 디렉토리명 추출
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

# 조치 파일 실행 함수
def run_fix_script(script_path, json_output_path, 담당자, log_file_path):
    try:
        result = subprocess.run([python_cmd, script_path, 담당자], capture_output=True, text=True, check=True)
        fix_result = json.loads(result.stdout)

        with open(json_output_path, 'w', encoding='utf-8') as json_file:
            json.dump(fix_result, json_file, ensure_ascii=False, indent=4)

        log_message(log_file_path, f"조치 성공: {script_path}")
        return fix_result
    except Exception as e:
        log_message(log_file_path, f"조치 실패: {script_path} - 오류: {str(e)}")
        return None

# info.json 생성 메소드
def generate_info_json(result_dir, log_file_path):
    hwid = get_hwid()  # HWID 가져오기
    system_info = {
        "시설명": "주요정보통신기반시설1",
        "조치 시작일자": "",
        "조치 종료일자": "",
        "시스템 목록": [
            {
                "시스템 이름": socket.gethostname(),
                "IP 주소": socket.gethostbyname(socket.gethostname()),
                "운영 체제": platform.system(),
                "운영 체제 버전": platform.version(),
                "지역": "서울",
                "HWID": hwid,
                "조치 항목": {}
            }
        ]
    }

    info_json_path = os.path.join(result_dir, "info.json")
    with open(info_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(system_info, json_file, ensure_ascii=False, indent=4)

    log_message(log_file_path, f"info.json 생성 완료: {info_json_path}")
    return info_json_path

# 조치 파일과 info.json을 통합하는 make_json 메소드
def make_json(result_dir, log_file_path):
    combined_result = {}

    # info.json 읽어오기
    info_json_path = os.path.join(result_dir, "info.json")
    with open(info_json_path, 'r', encoding='utf-8') as info_file:
        combined_result = json.load(info_file)

    fix_results = {}
    earliest_time = None
    latest_time = None

    for file_name in os.listdir(result_dir):
        if file_name.endswith('.json') and file_name != 'info.json':
            with open(os.path.join(result_dir, file_name), 'r', encoding='utf-8') as json_file:
                fix_result = json.load(json_file)

                code = fix_result.get("코드")
                if code and fix_result.get("조치 결과"):
                    fix_time = fix_result.get("조치 시각")

                    fix_results[code] = {
                        "카테고리": fix_result.get("카테고리"),
                        "항목 설명": fix_result.get("항목 설명"),
                        "중요도": "상",
                        "진단 결과": fix_result.get("진단 결과"),
                        "조치 결과": fix_result.get("조치 결과"),
                        "재진단 결과": fix_result.get("재진단 결과"),
                        "메시지": fix_result.get("메시지"),
                        "조치파일명": fix_result.get("조치 파일명"),
                        "조치 담당자": fix_result.get("조치 담당자"),
                        "조치 시각": fix_time
                    }

                    if fix_time:
                        fix_time_obj = datetime.strptime(fix_time, "%Y-%m-%d %H:%M:%S")

                        if earliest_time is None or fix_time_obj < earliest_time:
                            earliest_time = fix_time_obj

                        if latest_time is None or fix_time_obj > latest_time:
                            latest_time = fix_time_obj

    if combined_result.get("시스템 목록") and fix_results:
        combined_result["시스템 목록"][0]["조치 항목"] = fix_results

    # 조치 시작일과 종료일 설정
    if earliest_time:
        combined_result["조치 시작일"] = earliest_time.strftime("%Y-%m-%d %H:%M:%S")
    if latest_time:
        combined_result["조치 종료일"] = latest_time.strftime("%Y-%m-%d %H:%M:%S")

    combined_output_path = os.path.join(result_dir, f"{datetime.now().strftime('%Y%m%d')}_조치결과통합.json")
    with open(combined_output_path, 'w', encoding='utf-8') as json_file:
        json.dump(combined_result, json_file, ensure_ascii=False, indent=4)

    log_message(log_file_path, f"통합 JSON 파일 생성 완료: {combined_output_path}")

# 진단 디렉토리 리스트 출력 및 선택 (Log 디렉토리는 제외)
def get_diagnosis_directory():
    dirs = [d for d in os.listdir(result_base_dir) if d != "Log"]
    if not dirs:
        print("선택 가능한 진단 디렉토리가 없습니다.")
        return None
    
    print("진단 디렉토리를 선택하세요:")
    for i, directory in enumerate(dirs):
        print(f"{i + 1}. {directory}")
    
    선택 = int(input("번호를 입력하세요: ").strip()) - 1
    return os.path.join(result_base_dir, dirs[선택])

# 진단 결과 중 취약 항목 필터링
def filter_vulnerabilities(diagnosis_file):
    with open(diagnosis_file, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    vulnerable_items = []
    for code, item in data["시스템 목록"][0]["진단 항목"].items():
        if item["진단 결과"] == "취약":
            vulnerable_items.append((code, item))

    return vulnerable_items

# 메인 실행 함수
def main():
    diagnosis_dir = get_diagnosis_directory()

    diagnosis_file = None
    for file_name in os.listdir(diagnosis_dir):
        if "진단결과통합" in file_name:
            diagnosis_file = os.path.join(diagnosis_dir, file_name)
            break

    if not diagnosis_file:
        print("진단결과통합 파일을 찾을 수 없습니다.")
        return

    vulnerabilities = filter_vulnerabilities(diagnosis_file)
    if not vulnerabilities:
        print("취약 항목이 없습니다.")
        return

    print("취약 항목 리스트:")
    for code, item in vulnerabilities:
        print(f"{code}: {item['항목 설명']}")

    조치자 = input("조치자의 이름을 입력하세요: ").strip()

    action_dir = os.path.join(action_base_dir, os.path.basename(diagnosis_dir))
    if not os.path.exists(action_dir):
        os.makedirs(action_dir)

    log_file_path = create_log_file_path(action_dir)

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    generate_info_json(action_dir, log_file_path)

    for code, item in vulnerabilities:
        script_path = os.path.join(fix_script_base_dir, f"{int(code.split('-')[1])}.py")
        json_output_path = os.path.join(action_dir, f"{int(code.split('-')[1])}.json")
        run_fix_script(script_path, json_output_path, 조치자, log_file_path)

    # 통합 JSON 생성 여부 묻기
    while True:
        통합_응답 = input("통합 JSON 파일을 생성하시겠습니까? (y/n): ").strip().lower()

        # 올바른 입력인지 확인
        if 통합_응답 in ['y', 'n', '']:
            break
        else:
            print("잘못된 입력입니다. 다시 시도하세요.")

    if 통합_응답 == 'y' or 통합_응답 == '':
        make_json(action_dir, log_file_path)
        log_message(log_file_path, f"조치 완료. \n결과는 {action_base_dir}에 저장되었습니다.")
    else:
        log_message(log_file_path, f"통합 JSON 파일 생성을 건너뜁니다. \n조치 완료. \n결과는 {action_base_dir}에 저장되었습니다.")


    log_message(log_file_path, f"로그는 {log_file_path}에 저장되었습니다.")

if __name__ == "__main__":
    main()