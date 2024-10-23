import os
import json
from collections import defaultdict

# JSON 파일을 읽고 병합된 결과를 저장할 딕셔너리
merged_results = {}

# JSON 파일을 병합하는 함수
def merge_json(data):
    facility_name = data["시설명"]

    # 시설명이 없으면 초기화
    if facility_name not in merged_results:
        merged_results[facility_name] = {
            "시설명": facility_name,
            "진단 시작일자": data["진단 시작일자"],
            "진단 종료일자": data["진단 종료일자"],
            "시스템 목록": []
        }

    # 진단 시작일자와 종료일자를 갱신
    current_start_date = merged_results[facility_name]["진단 시작일자"]
    current_end_date = merged_results[facility_name]["진단 종료일자"]

    if data["진단 시작일자"] < current_start_date:
        merged_results[facility_name]["진단 시작일자"] = data["진단 시작일자"]

    if data["진단 종료일자"] > current_end_date:
        merged_results[facility_name]["진단 종료일자"] = data["진단 종료일자"]

    # 시스템 목록 추가 (중복 시스템명도 그대로 추가)
    merged_results[facility_name]["시스템 목록"].extend(data["시스템 목록"])

# 지정된 디렉토리에서 파일명에 '진단결과통합' 또는 '조치결과통합'이 포함된 json 파일을 찾아서 처리하는 함수
def process_json_files(directory, file_keyword):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file_keyword in file and file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    merge_json(data)

# 사용자로부터 입력을 받아 경로 선택
def select_directory():
    while True:
        print("어떤 데이터를 통합하시겠습니까?")
        print("1. 진단결과")
        print("2. 조치결과")
        print("3. 프로그램 종료")
        
        choice = input("선택 (1, 2, 또는 3): ").strip()
        
        if choice == "1":
            return os.path.join('.', '3. 진단결과'), '진단결과통합', '진단결과_integration'
        elif choice == "2":
            return os.path.join('.', '4. 조치결과'), '조치결과통합', '조치결과_integration'
        elif choice == "3":
            print("프로그램을 종료합니다.")
            exit()
        else:
            print("잘못된 입력입니다. 다시 입력해주세요.")

# 시퀀스를 추가하여 파일명 중복 방지
def get_unique_filename(directory, base_name):
    index = 1
    while True:
        file_name = f"{base_name}_{index}.json"
        file_path = os.path.join(directory, file_name)
        if not os.path.exists(file_path):
            return file_path
        index += 1

def flatten_json(file_path, output_path):
    # 파일을 읽어서 JSON 데이터로 변환
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    flattened = []

    # 데이터가 리스트인지 확인
    if isinstance(data, list):
        # 리스트라면 각 항목에 대해 처리
        for item in data:
            # 시스템 목록에 접근 (각각의 시스템)
            if "시스템 목록" in item:
                for system in item["시스템 목록"]:
                    system_name = system["시스템 이름"]
                    ip_address = system["IP 주소"]
                    os = system["운영 체제"]
                    os_version = system["운영 체제 버전"]
                    system_uuid = system["시스템 UUID"]
                    location = system["지역"]

                    # 진단 항목을 개별 객체로 변환하여 배열에 추가
                    for key, diagnostic in system["진단 항목"].items():
                        flattened.append({
                            "시설명": item["시설명"],
                            "진단_시작일자": item["진단 시작일자"],
                            "진단_종료일자": item["진단 종료일자"],
                            "시스템_이름": system_name,
                            "IP_주소": ip_address,
                            "운영_체제": os,
                            "운영_체제_버전": os_version,
                            "시스템_UUID": system_uuid,
                            "지역": location,
                            "진단항목": key,
                            "카테고리": diagnostic["카테고리"],
                            "항목_설명": diagnostic["항목 설명"],
                            "중요도": diagnostic["중요도"],
                            "진단_결과": diagnostic["진단 결과"],
                            "진단_파일명": diagnostic["진단 파일명"],
                            "진단_담당자": diagnostic["진단 담당자"],
                            "진단_시각": diagnostic["진단 시각"]
                        })
    else:
        print("올바른 리스트 형태의 JSON 데이터를 입력하세요.")

    # 변환된 데이터를 output_path에 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(flattened, f, ensure_ascii=False, indent=4)

    print(f"Flattened JSON 파일이 {output_path}에 저장되었습니다.")

# 프로그램 실행
if __name__ == "__main__":

    # 경로와 파일 키워드, 출력 파일명 베이스 선택
    input_directory, file_keyword, output_base_name = select_directory()
    
    # 결과 저장할 경로
    output_directory = os.path.join('.', '최종통합본')

    # JSON 파일 처리 실행
    process_json_files(input_directory, file_keyword)

    # 출력할 파일 경로 생성 (중복 방지 파일명 생성)
    output_file_path_integrated = get_unique_filename(output_directory, output_base_name)
    output_file_path_flattened = get_unique_filename(output_directory, output_base_name.replace("integration", "flattened"))

    # 최종통합본 폴더가 없으면 생성
    os.makedirs(output_directory, exist_ok=True)

    # 원본 병합된 결과 저장 (진단결과_integration_1.json 형식)
    with open(output_file_path_integrated, 'w', encoding='utf-8') as output_file:
        json.dump(list(merged_results.values()), output_file, ensure_ascii=False, indent=4)

    print(f"통합 결과가 {output_file_path_integrated}에 저장되었습니다.")

    # 병합된 파일을 읽어들여 평탄화된 결과 생성 및 저장
    flattened_data = flatten_json(output_file_path_integrated, output_file_path_flattened)