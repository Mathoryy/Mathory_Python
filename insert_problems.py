# insert_problems.py

import os
import json
import pymysql # MySQL 데이터베이스와 파이썬을 연결해주는 라이브러리
from tqdm import tqdm # 진행 상황을 시각적으로 보여주는 라이브러리
from config import MYSQL  # DB 접속 정보 불러오기

# MySQL 연결
conn = pymysql.connect(**MYSQL)
cursor = conn.cursor()
log_file = open("error_log_problems.txt", "w", encoding="utf-8")


# 라벨링 데이터 폴더 경로
labeling_root = './수학 과목 문제생성 데이터/02.라벨링데이터'

# TL_1. 으로 시작하는 모든 문제 폴더 자동 탐색
problem_dirs = [os.path.join(labeling_root, d)
   for d in os.listdir(labeling_root) # labeling_root 폴더 내의 모든 파일 및 폴더 목록 리스트로 반환해서 꺼내기
   if d.startswith('TL_1.') # 파일명 또는 폴더명이 'TL_1.'으로 시작하는지 검사
   and os.path.isdir(os.path.join(labeling_root, d)) # 폴더 이름 결합 후 경로로 완성
]
# 결과 예시
""" [
   './02.라벨링데이터/TL_1.문제_중학교_1학년',
   './02.라벨링데이터/TL_1.문제_중학교_2학년',
   './02.라벨링데이터/TL_1.문제_초등학교_3학년',
   ...
] """

# 성공/실패 건수 통계 초기화
total_files = 0
total_inserted = 0
total_failed = 0

# 각 폴더 안의 JSON 파일 처리
for json_dir in problem_dirs: # 전체 경로 리스트에서  각 폴더를 하나씩 반복하며 JSON 파일들을 처리\
   
   # 해당 폴더 안에 .json 파일들만 리스트로 가져오기
   files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
   
   # files 리스트를 반복하면서, 각 fname을 처리
   for fname in tqdm(files, desc=f"{os.path.basename(json_dir)} 삽입 중"):
      # 현재 처리 중인 JSON 파일의 전체 경로를 path에 저장
      path = os.path.join(json_dir, fname)
      total_files += 1 # 파일 수 카운트

      try:
         with open(path, 'r', encoding='utf-8') as f: # JSON 파일 열기 및 객체로(f) 받음
            data = json.load(f) # JSON 파일을 파이썬 객체로 변환
            qid = data['id'] # 문제 ID 저장

            # 중복 확인
            cursor.execute("SELECT COUNT(*) FROM math_problem WHERE id = %s", (qid,))
            exists = cursor.fetchone()[0] > 0
            if exists:
               continue

         qfile = data.get('question_filename') # 이미지파일이름
         qinfo = data['question_info'][0] # 문제정보
         ocr = data['OCR_info'][0] # 문제 OCR 정보

         # 위에서 추출한 데이터 DB 테이블에 삽입
         cursor.execute("""
            INSERT INTO math_problem (
               id, grade, term, unit, topic_code, topic_name,
               type1, type2, question_condition, step, sector1, sector2, contents,
               question_text, figure_text, image_file
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
         """, (
            qid,
            qinfo.get('question_grade'),
            qinfo.get('question_term'),
            qinfo.get('question_unit'),
            qinfo.get('question_topic'),
            qinfo.get('question_topic_name'),
            qinfo.get('question_type1'),
            qinfo.get('question_type2'),
            qinfo.get('question_condition'),
            qinfo.get('question_step'),
            qinfo.get('question_sector1'),
            qinfo.get('question_sector2'),
            qinfo.get('question_contents'),
            ocr.get('question_text'),
            ocr.get('figure_text'),
            qfile
         ))
         total_inserted += 1

      except Exception as e:
         total_failed += 1
         error_msg = f"❌ 오류 - {fname} in {json_dir} : {e}"
         print(error_msg)
         log_file.write(error_msg + "\n")

conn.commit() # 모든 INSERT를 최종 저장
conn.close() # DB 연결 종료
log_file.close()   # 로그 파일 닫기


# 통계 출력
print("\n📊 문제 삽입 결과")
print(f"총 파일 수        : {total_files}")
print(f"삽입 성공         : {total_inserted}")
print(f"삽입 실패 (에러)  : {total_failed}")
print("✅ 전체 삽입 작업 완료")
