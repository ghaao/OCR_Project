import logging
import logging.handlers
import os

# 현재 파일 경로 및 파일명 찾기
current_dir = os.path.dirname(os.path.realpath(__file__))
current_file = os.path.basename(__file__)
current_file_name = current_file[:-3]  # xxxx.py
LOG_FILENAME = 'log-{}'.format(current_file_name)

# 로그 저장할 폴더 생성
log_dir = '{}/logs'.format(current_dir)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

#log settings
formatter = logging.Formatter(
  '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s'
  )

#handler settings
file_handler = logging.handlers.TimedRotatingFileHandler(
  filename=LOG_FILENAME, when='midnight', interval=1,  encoding='utf-8'
  ) # 자정마다 한 번씩 로테이션
file_handler.setFormatter(formatter) # 핸들러에 로깅 포맷 할당
file_handler.suffix = 'log-%Y%m%d' # 로그 파일명 날짜 기록 부분 포맷 지정

# 로거 생성
Logger = logging.getLogger()
Logger.setLevel(logging.INFO)
Logger.addHandler(file_handler) # 로거에 핸들러 추가

def logging(msg):
    Logger.debug(msg)
