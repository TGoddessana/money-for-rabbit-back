from datetime import datetime
import pytz

MESSAGE_OPEN_DATETIME = datetime(2023, 1, 10, tzinfo=pytz.timezone("Asia/Seoul"))


def get_korean_datetime():
    return datetime.now(pytz.timezone("Asia/Seoul"))
