import enum


@enum.unique
class FiddlerTimestamp(str, enum.Enum):
    """Supported timestamp formats for events published to Fiddler"""

    EPOCH_MILLISECONDS = 'epoch milliseconds'
    EPOCH_SECONDS = 'epoch seconds'
    ISO_8601 = '%Y-%m-%d %H:%M:%S.%f'
    TIMEZONE = ISO_8601 + '%Z %z'
    INFER = 'infer'


@enum.unique
class FileType(str, enum.Enum):
    """Supported file types for ingestion"""

    CSV = '.csv'


@enum.unique
class ServerDeploymentMode(str, enum.Enum):
    F1 = 'f1'
    F2 = 'f2'


@enum.unique
class UploadType(str, enum.Enum):
    """To distinguish between dataset ingestion and event ingestion.
    Supposed to be only internally used.
    """

    DATASET = 'dataset'
    EVENT = 'event'
