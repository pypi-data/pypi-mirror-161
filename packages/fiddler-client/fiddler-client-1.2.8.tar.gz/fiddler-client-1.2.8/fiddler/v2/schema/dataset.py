from typing import List, Optional

from fiddler.v2.constants import FileType, UploadType
from fiddler.v2.schema.base import BaseDataSchema
from fiddler.v2.schema.common import DatasetInfo


class Dataset(BaseDataSchema):

    id: int
    name: str
    version: str
    file_list: dict
    info: DatasetInfo
    organization_name: str
    project_name: str


class DatasetIngest(BaseDataSchema):
    name: str
    file_name: List[str]
    info: Optional[DatasetInfo] = None
    file_type: Optional[FileType] = None
    file_schema: Optional[dict] = None
    upload_type = UploadType.DATASET

    class Config:
        use_enum_values = True
