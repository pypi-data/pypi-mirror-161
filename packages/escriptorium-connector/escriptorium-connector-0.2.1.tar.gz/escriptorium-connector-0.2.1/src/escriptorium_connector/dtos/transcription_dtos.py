from escriptorium_connector.utils.pydantic_dataclass_fix import dataclass
from escriptorium_connector.dtos.super_dtos import PagenatedResponse
from typing import Union, List
from datetime import datetime
from dataclasses import field


@dataclass(init=True, frozen=True)
class CharacterGraph:
    c: str
    poly: List[List[int]]
    confidence: float


@dataclass(init=True, frozen=True)
class PostAbbreviatedTranscription:
    name: str


@dataclass(init=True, frozen=True)
class GetAbbreviatedTranscription:
    pk: int
    name: str
    archived: bool = False
    avg_confidence: Union[float, None] = None


@dataclass(init=True, frozen=True)
class PostTranscription:
    line: int
    transcription: int
    content: str
    graphs: List[CharacterGraph] = field(default_factory=list)

@dataclass(init=True, frozen=True)
class PutTranscription:
    line: int
    pk: int
    transcription: int
    content: str
    graphs: List[CharacterGraph] = field(default_factory=list)

@dataclass(init=True, frozen=True)
class GetVersionData:
    graphs: Union[None, List[List[int]]]
    content: str
    avg_confidence: Union[float, None] = None


@dataclass(init=True, frozen=True)
class GetVersion:
    data: GetVersionData
    author: str
    source: str
    revision: str
    created_at: datetime
    updated_at: datetime


@dataclass(init=True, frozen=True)
class GetTranscription:
    pk: int
    line: int
    transcription: int
    content: str
    versions: List[GetVersion]
    version_author: str
    version_source: str
    version_updated_at: datetime
    graphs: Union[None, List[CharacterGraph]] = field(default_factory=list)
    avg_confidence: Union[float, None] = None


@dataclass
class GetTranscriptions(PagenatedResponse):
    results: List[GetTranscription] = field(default_factory=list)

@dataclass(init=True, frozen=True)
class PostBulkCreateTranscriptions:
    status: str
    lines: List[GetTranscription] = field(default_factory=list)
