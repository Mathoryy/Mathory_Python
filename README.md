# Mathory_Python
파이썬 코드

## 데이터 제공
Python + FastAPI + Uvicorn (AI Hub 수학 문제 제공)

# 📂 math-data-loader 디렉토리 구조

AI Hub 수학 문제 데이터를 로컬 이미지 및 JSON 파일 형태로 관리하고, 이를 MySQL DB에 삽입하기 위한 프로젝트 디렉토리입니다.


## 📁 디렉토리/파일 설명

- **images/**  
  수학 문제 이미지 파일이 저장되는 폴더입니다.  
  예: `M2_2_06_00041_39637.png`

- **json/**  
  각 문제에 해당하는 JSON 형식의 메타데이터 및 문제 정보가 저장됩니다.  
  예: `M2_2_06_00041_39637.json`

- **config.py**  
  MySQL DB 연결을 위한 설정 (호스트, 포트, 사용자명, 비밀번호, DB 이름 등)을 포함한 파이썬 파일입니다.

- **insert_problems.py**  
  JSON 데이터를 파싱하여 MySQL DB에 삽입하는 메인 실행 코드입니다.

- **requirements.txt**  
  실행에 필요한 파이썬 패키지 목록 (`pymysql`, `json`, 등) 이 정의된 파일입니다.

