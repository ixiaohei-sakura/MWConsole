import os
import time
import logging
import re
from logging.handlers import TimedRotatingFileHandler


class MLogger:
    def __init__(self, name='MWC'):
        self.name = name
        self._logger = self._setup_log_file(name)

    def _get_time(self) -> str:
        return time.strftime("%H:%M:%S", time.localtime())

    def _setup_log_file(self, name: str):
        logger = logging.getLogger(name)
        if os.path.isdir('./log') is not True:
            os.mkdir('./log')
        log_path = './log/latest.log'
        logger.setLevel(logging.INFO)
        file_handler = TimedRotatingFileHandler(filename=log_path, when="MIDNIGHT", interval=1, backupCount=30)
        file_handler.suffix = "%Y-%m-%d.log"
        file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
        file_handler.setFormatter(logging.Formatter(
            "[%(asctime)s][%(module)s.%(funcName)s(%(filename)s:%(lineno)d)][%(process)d][%(levelname)s]:%(message)s"))
        logger.addHandler(file_handler)
        return logger

    def logger(self, level: int, data: str, name='Main', end='\n'):
        now_time = self._get_time()
        if len(data) == 0:
            return
        for i in range(100):
            if i == 0: i = 1
            data = data.replace('\n' * i, '')
        for i in range(100):
            if i == 0: i = 1
            data = data.replace('\r' * i, '')
        if level == 0:
            print(f'[\033[1;32m{self.name}\033[0m][{now_time}][{name}/\033[1;32mINFO\033[0m]: {data}', end=end)
            self._logger.info(data)
        elif level == 1:
            print(f'[\033[1;32m{self.name}\033[0m][{now_time}][{name}/\033[1;33mWARN\033[0m]: {data}', end=end)
            self._logger.warning(data)
        elif level == 2:
            print(f'[\033[1;32m{self.name}\033[0m][{now_time}][{name}/\033[1;31mERROR\033[0m]: {data}', end=end)
            self._logger.error(data)
        elif level == 3:
            print(f'[\033[1;32m{self.name}\033[0m][{now_time}][{name}/\033[1;34mDEBUG\033[0m]: \033[1;34m{data}\033[0m', end=end)
            self._logger.debug(data)
        elif level == 4:
            print(f'[\033[1;32m{self.name}\033[0m][{now_time}][{name}/\033[1;31mCRITICAL\033[0m]: {data}', end=end)
            self._logger.critical(data)

    @property
    def get_logger_(self):
        return self._logger
