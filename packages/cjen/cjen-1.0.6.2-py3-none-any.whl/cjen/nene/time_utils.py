import datetime


class TimeUtils:
    @staticmethod
    def calculate_day_date(start_date: datetime.date, spend_days=[]):
        for spend_day in spend_days:
            print(spend_day, start_date)
            count = 0
            while count < spend_day:
                start_date = start_date + datetime.timedelta(days=1)
                if TimeUtils.is_weekend(start_date):
                    continue
                else:
                    count += 1

    @staticmethod
    def is_weekend(date: datetime.date):
        return (date.weekday() + 1) == 6 or (date.weekday() + 1) == 7


if __name__ == '__main__':
    start = datetime.datetime.strptime("2022-05-16", "%Y-%m-%d")
    TimeUtils.calculate_day_date(start, [
1,
2,
3,
4,
5,
5,
5,
3,
3,
4,
4,
5])