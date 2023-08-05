# This code parses date/times, so please
#
#     pip install python-dateutil
#
# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = crawler_run_metadata_from_dict(json.loads(json_string))

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, TypeVar, Type, cast
from datetime import datetime
import dateutil.parser


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class Platform(Enum):
    BIGQUERY = "BIGQUERY"
    DBT_MODEL = "DBT_MODEL"
    DOCUMENTDB = "DOCUMENTDB"
    DYNAMODB = "DYNAMODB"
    ELASTICSEARCH = "ELASTICSEARCH"
    EXTERNAL = "EXTERNAL"
    LOOKER = "LOOKER"
    LOOKER_EXPLORE = "LOOKER_EXPLORE"
    LOOKER_VIEW = "LOOKER_VIEW"
    METABASE = "METABASE"
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    POWER_BI = "POWER_BI"
    POWER_BI_DATASET = "POWER_BI_DATASET"
    RDS = "RDS"
    REDIS = "REDIS"
    REDSHIFT = "REDSHIFT"
    S3 = "S3"
    SNOWFLAKE = "SNOWFLAKE"
    TABLEAU = "TABLEAU"
    TABLEAU_DATASOURCE = "TABLEAU_DATASOURCE"
    THOUGHT_SPOT = "THOUGHT_SPOT"
    THOUGHT_SPOT_DATA_OBJECT = "THOUGHT_SPOT_DATA_OBJECT"
    UNKNOWN = "UNKNOWN"


class Status(Enum):
    FAILURE = "FAILURE"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"


@dataclass
class CrawlerRunMetadata:
    """Metadata of a crawler run"""
    crawler_name: Optional[str] = None
    description: Optional[str] = None
    end_time: Optional[datetime] = None
    entity_count: Optional[float] = None
    error_message: Optional[str] = None
    log_file: Optional[str] = None
    platform: Optional[Platform] = None
    stack_trace: Optional[str] = None
    start_time: Optional[datetime] = None
    status: Optional[Status] = None

    @staticmethod
    def from_dict(obj: Any) -> 'CrawlerRunMetadata':
        assert isinstance(obj, dict)
        crawler_name = from_union([from_str, from_none], obj.get("crawlerName"))
        description = from_union([from_str, from_none], obj.get("description"))
        end_time = from_union([from_datetime, from_none], obj.get("endTime"))
        entity_count = from_union([from_float, from_none], obj.get("entityCount"))
        error_message = from_union([from_str, from_none], obj.get("errorMessage"))
        log_file = from_union([from_str, from_none], obj.get("logFile"))
        platform = from_union([Platform, from_none], obj.get("platform"))
        stack_trace = from_union([from_str, from_none], obj.get("stackTrace"))
        start_time = from_union([from_datetime, from_none], obj.get("startTime"))
        status = from_union([Status, from_none], obj.get("status"))
        return CrawlerRunMetadata(crawler_name, description, end_time, entity_count, error_message, log_file, platform, stack_trace, start_time, status)

    def to_dict(self) -> dict:
        result: dict = {}
        result["crawlerName"] = from_union([from_str, from_none], self.crawler_name)
        result["description"] = from_union([from_str, from_none], self.description)
        result["endTime"] = from_union([lambda x: x.isoformat(), from_none], self.end_time)
        result["entityCount"] = from_union([to_float, from_none], self.entity_count)
        result["errorMessage"] = from_union([from_str, from_none], self.error_message)
        result["logFile"] = from_union([from_str, from_none], self.log_file)
        result["platform"] = from_union([lambda x: to_enum(Platform, x), from_none], self.platform)
        result["stackTrace"] = from_union([from_str, from_none], self.stack_trace)
        result["startTime"] = from_union([lambda x: x.isoformat(), from_none], self.start_time)
        result["status"] = from_union([lambda x: to_enum(Status, x), from_none], self.status)
        return result


def crawler_run_metadata_from_dict(s: Any) -> CrawlerRunMetadata:
    return CrawlerRunMetadata.from_dict(s)


def crawler_run_metadata_to_dict(x: CrawlerRunMetadata) -> Any:
    return to_class(CrawlerRunMetadata, x)
