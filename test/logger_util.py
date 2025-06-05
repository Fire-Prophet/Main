# logger_util.py
import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

def setup_logger(name, log_file, level=logging.INFO, console_output=True,
                 max_bytes=10*1024*1024, backup_count=5, rotation_interval=1,
                 rotation_unit='midnight'):
    """
    로깅 설정을 구성합니다.
    로그 파일, 레벨, 콘솔 출력 여부, 파일 회전(rotation) 설정을 지정할 수 있습니다.
    :param name: 로거의 이름.
    :param log_file: 로그 파일 경로.
    :param level: 로깅 레벨 (e.g., logging.INFO, logging.DEBUG).
    :param console_output: 콘솔에도 로그를 출력할지 여부.
    :param max_bytes: RotatingFileHandler를 위한 최대 로그 파일 크기 (바이트).
    :param backup_count: RotatingFileHandler를 위한 백업 파일 수.
    :param rotation_interval: TimedRotatingFileHandler를 위한 회전 간격.
    :param rotation_unit: TimedRotatingFileHandler를 위한 회전 단위 ('H', 'M', 'S', 'D', 'midnight').
    :return: 구성된 로거 객체.
    """
    # 로그 디렉토리 생성
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 로거 인스턴스 생성
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 핸들러 중복 방지
    if not logger.handlers:
        # 파일 핸들러 (크기 기반 회전)
        # file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
        # 파일 핸들러 (시간 기반 회전)
        file_handler = TimedRotatingFileHandler(
            log_file,
            when=rotation_unit, # 'midnight', 'H', 'M', 'S', 'D', 'W0'-'W6'
            interval=rotation_interval,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 콘솔 핸들러 (선택 사항)
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    return logger

# 예시 사용
if __name__ == "__main__":
    # 'app_logs' 디렉토리에 'my_app.log' 파일로 로그를 기록하도록 설정
    # 매일 자정마다 로그 파일 회전, 5개의 백업 파일 유지
    my_logger = setup_logger(
        name='my_app_logger',
        log_file='app_logs/my_app.log',
        level=logging.DEBUG,
        console_output=True,
        rotation_unit='midnight',
        rotation_interval=1
    )

    my_logger.debug("This is a debug message.")
    my_logger.info("This is an info message.")
    my_logger.warning("This is a warning message.")
    my_logger.error("This is an error message.")
    my_logger.critical("This is a critical message.")

    # 다른 로거 인스턴스 생성 (다른 파일에 기록)
    another_logger = setup_logger(
        name='another_module_logger',
        log_file='app_logs/another_module.log',
        level=logging.WARNING,
        console_output=False,
        max_bytes=1024, # 1KB
        backup_count=3,
        rotation_unit='H' # 시간별 회전 (테스트용으로 작게 설정)
    )

    another_logger.info("This info message will NOT be shown due to WARNING level.")
    another_logger.warning("This is a warning from another module.")
    another_logger.error("This is an error from another module.")

    # 생성된 로그 파일 확인: app_logs/ 디렉토리에 파일이 생성됩니다.
