import logging
from logging import handlers
from pathlib import Path

FILE_PATH = str(Path(__file__).parent.resolve())

print(FILE_PATH)

# 按时间分割文件
logger = logging.getLogger() 
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s : %(message)s")
log_file_handler = handlers.TimedRotatingFileHandler(filename=FILE_PATH + "/log", when="M", interval=1, backupCount=1, encoding='utf-8')
log_file_handler.setFormatter(formatter)
# log_file_handler.setLevel(logging.DEBUG)
log_file_handler.suffix += ".log"
logger.addHandler(log_file_handler)


logger.critical('测试- critical')
logger.error('测试 error')
logger.warning('测试 warning')
logger.info('测试 info')
logger.debug('测试 debug')

