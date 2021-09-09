import datetime


class LogRecord:

    def __init__(self, time, user_name, message):
        self.time = time
        self.user_name = user_name
        self.message = message

    @staticmethod
    def to_session(user_name: str, is_edit_session: bool, start_session_time: datetime.datetime,
                   end_session_time: datetime.datetime, start_edit_time: datetime.datetime,
                   end_edit_time: datetime.datetime):
        return {
            "user_name": user_name,
            "session_duration(second)": (end_session_time - start_session_time).total_seconds(),
            "is_edit_session": is_edit_session,
            "start_session_time": start_session_time.strftime('%Y%m%dT%H%M%S'),
            "end_session_time": end_session_time.strftime('%Y%m%dT%H%M%S'),
            "edit_duration(second)": (end_edit_time - start_edit_time).total_seconds(),
            "events": []
        }

    @staticmethod
    def to_single_event(event_time: datetime.datetime, event_message: str):
        return {
            "timestamp": event_time.strftime('%Y%m%dT%H%M%S'),
            "event_message": event_message
        }
