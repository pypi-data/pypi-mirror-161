from typing import List, Optional

from fiddler.v2.constants import FiddlerTimestamp, FileType, UploadType
from fiddler.v2.schema.base import BaseDataSchema


class EventsIngest(BaseDataSchema):
    file_name: List[str]
    batch_id: Optional[str] = None
    events_schema: Optional[dict] = None
    id_field: Optional[str] = None
    is_update: Optional[bool] = None
    timestamp_field: Optional[str] = None
    timestamp_format: Optional[FiddlerTimestamp] = None
    group_by: Optional[str] = None
    file_type: Optional[FileType] = None
    upload_type = UploadType.EVENT

    class Config:
        use_enum_values = True


class EventIngest(BaseDataSchema):
    event: dict
    event_id: Optional[str] = None
    id_field: Optional[str] = None
    is_update: Optional[bool] = None
    event_timestamp: Optional[str] = None
    timestamp_format: Optional[FiddlerTimestamp] = None
