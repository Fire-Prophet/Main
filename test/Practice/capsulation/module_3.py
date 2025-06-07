import datetime

class DateHelper:
    def get_current_date(self):
        return datetime.date.today()

    def format_date(self, date_obj, format_string="%Y-%m-%d"):
        return date_obj.strftime(format_string)
