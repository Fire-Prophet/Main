# datetime_formatter.py
from datetime import datetime, timedelta
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def format_datetime(dt_object, format_string="%Y-%m-%d %H:%M:%S"):
    """
    datetime 객체를 지정된 형식의 문자열로 변환합니다.
    """
    if not isinstance(dt_object, datetime):
        logging.error(f"Input is not a datetime object: {type(dt_object)}")
        raise TypeError("Input must be a datetime object.")
    try:
        formatted_str = dt_object.strftime(format_string)
        logging.info(f"Datetime object formatted to '{format_string}': {formatted_str}")
        return formatted_str
    except Exception as e:
        logging.error(f"Error formatting datetime object {dt_object} with format '{format_string}': {e}")
        return None

def parse_datetime_string(dt_string, format_string="%Y-%m-%d %H:%M:%S"):
    """
    지정된 형식의 날짜/시간 문자열을 datetime 객체로 파싱합니다.
    """
    if not isinstance(dt_string, str):
        logging.error(f"Input is not a string: {type(dt_string)}")
        raise TypeError("Input must be a string.")
    try:
        dt_object = datetime.strptime(dt_string, format_string)
        logging.info(f"Datetime string '{dt_string}' parsed to object: {dt_object}")
        return dt_object
    except ValueError as e:
        logging.error(f"Error parsing datetime string '{dt_string}' with format '{format_string}': {e}")
        return None

def add_days_to_date(dt_object, days):
    """
    datetime 객체에 지정된 일수를 더합니다.
    """
    if not isinstance(dt_object, datetime):
        logging.error(f"Input is not a datetime object: {type(dt_object)}")
        raise TypeError("Input must be a datetime object.")
    try:
        new_dt = dt_object + timedelta(days=days)
        logging.info(f"Added {days} days to {dt_object}. New date: {new_dt}")
        return new_dt
    except Exception as e:
        logging.error(f"Error adding {days} days to {dt_object}: {e}")
        return None

def get_current_datetime_utc():
    """
    현재 UTC 시각의 datetime 객체를 반환합니다.
    """
    current_utc = datetime.utcnow()
    logging.info(f"Current UTC datetime: {current_utc}")
    return current_utc

# 예시 사용
if __name__ == "__main__":
    now = datetime.now()
    print(f"Current datetime: {now}")

    # 다양한 형식으로 포맷팅
    formatted_date = format_datetime(now, "%Y/%m/%d")
    print(f"Formatted date (YYYY/MM/DD): {formatted_date}")

    formatted_time = format_datetime(now, "%H:%M:%S")
    print(f"Formatted time (HH:MM:SS): {formatted_time}")

    # 문자열 파싱
    date_str = "2023-10-26 14:30:00"
    parsed_dt = parse_datetime_string(date_str)
    if parsed_dt:
        print(f"Parsed datetime: {parsed_dt}")

    # 날짜 더하기
    future_date = add_days_to_date(now, 7)
    print(f"Date 7 days from now: {future_date}")

    # UTC 시각 가져오기
    utc_now = get_current_datetime_utc()
    print(f"Current UTC datetime: {utc_now}")

    # 잘못된 입력 예시
    # try:
    #     format_datetime("not a datetime", "%Y")
    # except TypeError as e:
    #     print(f"Caught error: {e}")
