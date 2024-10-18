import os
import json
from datetime import datetime

def make_json(result_dir, log_file_path, log_message):
    combined_result = {}

    # info.json 파일 읽기
    info_json_path = os.path.join(result_dir, "info.json")
    with open(info_json_path, 'r', encoding='utf-8') as info_file:
        combined_result = json.load(info_file)

    diagnosis_results = {}
    earliest_time = None
    latest_time = None

    # 진단 결과 파일들을 읽어서 저장
    for file_name in os.listdir(result_dir):
        if file_name.endswith('.json') and file_name != 'info.json':
            with open(os.path.join(result_dir, file_name), 'r', encoding='utf-8') as json_file:
                diagnosis_result = json.load(json_file)
                diagnosis_time = diagnosis_result.get("진단 시각")

                code = diagnosis_result.get("코드")
                diagnosis_results[code] = {
                    "카테고리": diagnosis_result.get("카테고리"),
                    "항목 설명": diagnosis_result.get("항목 설명"),
                    "중요도": diagnosis_result.get("중요도"),
                    "진단 결과": diagnosis_result.get("진단 결과"),
                    "진단 파일명": diagnosis_result.get("진단 파일명"),
                    "진단 담당자": diagnosis_result.get("진단 담당자"),
                    "진단 시각": diagnosis_time
                }

                if diagnosis_time:
                    diagnosis_time_obj = datetime.strptime(diagnosis_time, "%Y-%m-%d %H:%M:%S")

                    if earliest_time is None or diagnosis_time_obj < earliest_time:
                        earliest_time = diagnosis_time_obj

                    if latest_time is None or diagnosis_time_obj > latest_time:
                        latest_time = diagnosis_time_obj

    # 코드 기준으로 진단 결과 정렬
    diagnosis_results_sorted = dict(sorted(diagnosis_results.items(), key=lambda x: int(x[0].split('-')[-1])))

    # 시스템 목록에 정렬된 진단 항목 추가
    if combined_result.get("시스템 목록"):
        combined_result["시스템 목록"][0]["진단 항목"] = diagnosis_results_sorted

    # 진단 시작일자와 종료일자 설정
    if earliest_time:
        combined_result["진단 시작일자"] = earliest_time.strftime("%Y-%m-%d %H:%M:%S")
    if latest_time:
        combined_result["진단 종료일자"] = latest_time.strftime("%Y-%m-%d %H:%M:%S")

    # 통합 진단 결과 파일 저장
    combined_output_path = os.path.join(result_dir, f"{datetime.now().strftime('%Y%m%d')}_진단결과통합.json")
    with open(combined_output_path, 'w', encoding='utf-8') as json_file:
        json.dump(combined_result, json_file, ensure_ascii=False, indent=4)

    # 로그 메시지 기록
    log_message(log_file_path, f"통합 JSON 파일 생성 완료: {combined_output_path}")
