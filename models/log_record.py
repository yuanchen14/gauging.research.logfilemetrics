import datetime
import re
from enums.event_type import EventType

change_object_type_pattern = re.compile(r"(?P<undo>UNDO |)(?:changed object type to )(?P<object>'\S+')", re.IGNORECASE)
delete_points_pattern = re.compile(r"(?P<undo>UNDO |)(?:deleted )(?P<number>\d+)(?: point\(s\)| point)", re.IGNORECASE)
open_profile_pattern = re.compile(r"(?P<open>profile opened)|(?: in gauging editor )(?P<version_number>.*)",
                                  re.IGNORECASE)
change_attribute_pattern = re.compile(
    r"(?P<undo>UNDO |)(?:changed attribute )(?P<from_attr>\S+)(?: to )(?P<to_attr>\S+)", re.IGNORECASE)
change_offset_pattern = re.compile(r"(?P<undo>UNDO |)(?:changed offset to )(?P<offset>.*)", re.IGNORECASE)
move_points_pattern = re.compile(r"(?P<undo>UNDO |)(?:moved )(?P<number>\d+)(?: point\(s\))", re.IGNORECASE)
paste_pattern = re.compile(r"(?P<undo>UNDO |)(?:pasted points from profile )(?P<profile_name>.*)", re.IGNORECASE)
paste_drape_pattern = re.compile(r"(?P<undo>UNDO |)(?:pasted and draped points from profile )(?P<profile_name>.*)",
                                 re.IGNORECASE)
connect_lines_pattern = re.compile(r"(?P<undo>UNDO |)(?P<action>connected two lines)", re.IGNORECASE)
interpolate_all_points_pattern = re.compile(r"(?P<undo>UNDO |)(?P<action>interpolated all points)", re.IGNORECASE)
interpolate_points_pattern = re.compile(r"(?P<undo>UNDO |)(?P<action>interpolated points)", re.IGNORECASE)
add_point_pattern = re.compile(r"(?P<undo>UNDO |)(?P<action>added new point)", re.IGNORECASE)
merge_lines_pattern = re.compile(r"(?P<undo>UNDO |)(?P<action>merge two lines)", re.IGNORECASE)
swap_points_pattern = re.compile(r"(?P<undo>UNDO |)(?P<action>swap two points)", re.IGNORECASE)
drape_points_pattern = re.compile(r"(?P<undo>UNDO |)(?P<action>draped points)", re.IGNORECASE)
close_profile_pattern = re.compile(r"(?P<action>profile closed)", re.IGNORECASE)


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
        event_dictionary = {"timestamp": event_time.strftime('%Y%m%dT%H%M%S'), "event_message": event_message}
        change_object_type_match = change_object_type_pattern.match(event_message)
        delete_points_match = delete_points_pattern.match(event_message)
        open_profile_match = open_profile_pattern.match(event_message)
        change_attribute_match = change_attribute_pattern.match(event_message)
        change_offset_match = change_offset_pattern.match(event_message)
        move_points_match = move_points_pattern.match(event_message)
        paste_match = paste_pattern.match(event_message)
        paste_drape_match = paste_drape_pattern.match(event_message)
        connect_lines_match = connect_lines_pattern.match(event_message)
        interpolate_all_points_match = interpolate_all_points_pattern.match(event_message)
        interpolate_points_match = interpolate_points_pattern.match(event_message)
        add_point_match = add_point_pattern.match(event_message)
        merge_lines_match = merge_lines_pattern.match(event_message)
        swap_points_match = swap_points_pattern.match(event_message)
        drape_points_match = drape_points_pattern.match(event_message)
        close_profile_match = close_profile_pattern.match(event_message)
        if interpolate_all_points_match:
            if interpolate_all_points_match.group("undo"):
                event_dictionary["event_type"] = EventType.UndoInterpolatePointsProfile.value
            else:
                event_dictionary["event_type"] = EventType.InterpolatePointsProfile.value
        elif add_point_match:
            if add_point_match.group("undo"):
                event_dictionary["event_type"] = EventType.UndoAddPoint.value
            else:
                event_dictionary["event_type"] = EventType.AddPoint.value
        elif connect_lines_match:
            if connect_lines_match.group("undo"):
                event_dictionary["event_type"] = EventType.UndoConnectLinesPoint.value
            else:
                event_dictionary["event_type"] = EventType.ConnectLinesPoint.value
        elif interpolate_points_match:
            if interpolate_points_match.group("undo"):
                event_dictionary["event_type"] = EventType.UndoInterpolatePointsPoint.value
            else:
                event_dictionary["event_type"] = EventType.InterpolatePointsPoint.value
        elif merge_lines_match:
            if merge_lines_match.group("undo"):
                event_dictionary["event_type"] = EventType.UndoMergeLinesPoint.value
            else:
                event_dictionary["event_type"] = EventType.MergeLinesPoint.value
        elif swap_points_match:
            if swap_points_match.group("undo"):
                event_dictionary["event_type"] = EventType.UndoSwapTwoPoint.value
            else:
                event_dictionary["event_type"] = EventType.SwapTwoPoint.value
        elif drape_points_match:
            if drape_points_match.group("undo"):
                event_dictionary["event_type"] = EventType.UndoDrapePoint.value
            else:
                event_dictionary["event_type"] = EventType.DrapePoint.value
        elif close_profile_match:
            event_dictionary["event_type"] = EventType.CloseProfile.value
        elif change_object_type_match:
            if change_object_type_match.group("undo"):
                event_dictionary["event_type"] = EventType.UndoChangeObjectTypeProfile.value
                event_dictionary["extra_info"] = []
                event_dictionary["extra_info"].append(
                    {"object_after_changing": change_object_type_match.group("object"), "is_undo": True})
            else:
                event_dictionary["event_type"] = EventType.ChangeObjectTypeProfile.value
                event_dictionary["extra_info"] = []
                event_dictionary["extra_info"].append(
                    {"object_after_changing": change_object_type_match.group("object"), "is_undo": False})
        elif delete_points_match:
            if delete_points_match.group("undo"):
                event_dictionary["event_type"] = EventType.UndoDeletePoint.value
                event_dictionary["extra_info"] = []
                event_dictionary["extra_info"].append(
                    {"number_of_points": int(delete_points_match.group("number")), "is_undo": True})
            else:
                event_dictionary["event_type"] = EventType.DeletePoint.value
                event_dictionary["extra_info"] = []
                event_dictionary["extra_info"].append(
                    {"number_of_points": int(delete_points_match.group("number")), "is_undo": False})
        elif open_profile_match:
            event_dictionary["event_type"] = EventType.OpenProfile.value
            if open_profile_match.group("version_number"):
                event_dictionary["extra_info"] = []
                event_dictionary["extra_info"].append(
                    {"gauging_editor_version": open_profile_match.group("version_number")})
        elif change_attribute_match:
            if change_attribute_match.group("undo"):
                event_dictionary["event_type"] = EventType.UndoChangeAttributeProfile.value
                event_dictionary["extra_info"] = []
                event_dictionary["extra_info"].append({"attribute_before": change_attribute_match.group("from_attr"),
                                                       "attribute_after": change_attribute_match.group("to_attr"),
                                                       "is_undo": True})
            else:
                event_dictionary["event_type"] = EventType.ChangeAttributeProfile.value
                event_dictionary["extra_info"] = []
                event_dictionary["extra_info"].append({"attribute_before": change_attribute_match.group("from_attr"),
                                                       "attribute_after": change_attribute_match.group("to_attr"),
                                                       "is_undo": False})
        elif change_offset_match:
            if change_offset_match.group("undo"):
                event_dictionary["event_type"] = EventType.UndoChangeAttributeProfilee.value
                event_dictionary["extra_info"] = []
                event_dictionary["extra_info"].append(
                    {"offset": float(change_offset_match.group("offset")), "is_undo": True})
            else:
                event_dictionary["event_type"] = EventType.ChangeAttributeProfilee.value
                event_dictionary["extra_info"] = []
                event_dictionary["extra_info"].append(
                    {"offset": float(change_offset_match.group("offset")), "is_undo": False})
        elif move_points_match:
            event_dictionary["event_type"] = EventType.MovePoint.value
            event_dictionary["extra_info"] = []
            event_dictionary["extra_info"].append({"number_of_points": int(move_points_match.group("number"))})
        elif paste_match:
            if paste_match.group("undo"):
                event_dictionary["event_type"] = EventType.UndoPastePoint.value
                event_dictionary["extra_info"] = []
                event_dictionary["extra_info"].append(
                    {"pasted_profile_display_name": paste_match.group("profile_name"), "is_undo": True})
            else:
                event_dictionary["event_type"] = EventType.PastePoint.value
                event_dictionary["extra_info"] = []
                event_dictionary["extra_info"].append(
                    {"pasted_profile_display_name": paste_match.group("profile_name"), "is_undo": False})
        elif paste_drape_match:
            if paste_drape_match.group("undo"):
                event_dictionary["event_type"] = EventType.UndoPasteDrapePoint.value
                event_dictionary["extra_info"] = []
                event_dictionary["extra_info"].append(
                    {"pasted_draped_profile_display_name": paste_match.group("profile_name"), "is_undo": True})
            else:
                event_dictionary["event_type"] = EventType.PasteDrapePoint.value
                event_dictionary["extra_info"] = []
                event_dictionary["extra_info"].append(
                    {"pasted_draped_profile_display_name": paste_match.group("profile_name"), "is_undo": False})

        return event_dictionary
