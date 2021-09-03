from typing import Dict


class LogMetaData:

    def __init__(self, full_path, object_name, object_type, elr, track_id, profile_identifier):
        self.full_path = full_path
        self.object_name = object_name
        self.object_type = object_type
        self.track_id = track_id
        self.elr = elr
        self.profile_identifier = profile_identifier

    def to_record(self) -> Dict[str, str]:
        return {
            "profile_identifier": self.profile_identifier,
            "full_path": self.full_path,
            "object_name": self.object_name,
            "object_type": self.object_type,
            "elr": self.elr,
            "track_id": self.track_id
        }


class LogMetaDataWithDuration(LogMetaData):
    def __init__(self, full_path, object_name, object_type, elr, track_id, profile_identifier, duration):
        super().__init__(full_path, object_name, object_type, elr, track_id, profile_identifier)

        self.duration = duration

    def to_record(self) -> Dict[str, str]:
        dictionary_base = super().to_record()
        dictionary_base["duration(hrs)"] = self.duration
        return dictionary_base
