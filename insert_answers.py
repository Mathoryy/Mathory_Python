# insert_answers.py

import os
import json
import pymysql # MySQL 데이터베이스와 파이썬을 연결해주는 라이브러리
from tqdm import tqdm # 진행 상황을 시각적으로 보여주는 라이브러리
from config import MYSQL  # DB 접속 정보 불러오기

# MySQL 연결
conn = pymysql.connect(**MYSQL)
cursor = conn.cursor()
log_file = open("error_log_answers.txt", "w", encoding="utf-8")


# 라벨링 데이터의 루트 경로
labeling_root = './수학 과목 문제생성 데이터/02.라벨링데이터'

# TL_2.으로 시작하는 모든 모범답안 폴더를 자동 탐색
answer_dirs = [os.path.join(labeling_root, d) 
   for d in os.listdir(labeling_root) # labeling_root 폴더 내의 모든 파일 및 폴더 목록 리스트로 반환해서 꺼내기
   if d.startswith('TL_2.') # 파일명 또는 폴더명이 'TL_2.'으로 시작하는지 검사
   and os.path.isdir(os.path.join(labeling_root, d)) # 폴더 이름 결합 후 경로로 완성
]

# 성공/실패 건수 통계 초기화
total_files = 0
total_inserted = 0
total_failed = 0

# 각 폴더를 반복하며 모든 JSON 파일 처리
for json_dir in answer_dirs:
   files = [f for f in os.listdir(json_dir) if f.endswith('.json')]

   for fname in tqdm(files, desc=f"{os.path.basename(json_dir)} 삽입 중"):
      path = os.path.join(json_dir, fname)
      total_files += 1

      try:
         with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # 문제 ID = 외래키
            problem_id = data['id']
            ainfo = data['answer_info'][0] # 모범답안 정보

            # 중복 확인: 같은 문제_id와 answer_text 조합이 이미 있는지 확인
            cursor.execute("""
               SELECT COUNT(*) FROM model_answer
               WHERE problem_id = %s
            """, (problem_id))
            exists = cursor.fetchone()[0] > 0
            if exists:
               continue

         
         answer_text = ainfo.get('answer_text') # 답안 텍스트
         image_file = ainfo.get('answer_filename') or None

         cursor.execute("""
            INSERT INTO model_answer (
               problem_id, answer_text, image_file
            ) VALUES (%s, %s, %s)
         """, (
            problem_id, answer_text, image_file
         ))
         total_inserted += 1

      except Exception as e:
         total_failed += 1
         error_msg = f"❌ 오류 - {fname} in {json_dir} : {e}"
         print(error_msg)
         log_file.write(error_msg + "\n")

# 커밋 및 연결 종료
conn.commit()
conn.close()
log_file.close()   # 로그 파일 닫기

# 통계 출력
print("\n📊 모범답안 삽입 결과")
print(f"총 파일 수        : {total_files}")
print(f"삽입 성공         : {total_inserted}")
print(f"삽입 실패 (에러)  : {total_failed}")
print("✅ 전체 삽입 작업 완료")
