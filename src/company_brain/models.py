"""Strict input contracts. Trust metadata is supplied by the ingestion operator."""
from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Scope(Model):
    environment: str = Field(min_length=1, max_length=100)
    region: str = Field(min_length=1, max_length=100)


Kind = Literal["Service", "Job", "Workflow", "Team", "Person", "MigrationTask", "Decision"]
Predicate = Literal["RUNS_ON", "DEPENDS_ON", "REQUIRES", "OWNED_BY", "MIGRATION_TRACKED_BY", "BLOCKED_BY", "PERMITS_USE", "STATUS", "VERIFIED_CLEAR"]


def aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps require an explicit timezone")
    return value


class Entity(Model):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,100}$")
    kind: Kind
    name: str = Field(min_length=1, max_length=200)
    aliases: list[str] = Field(default_factory=list)
    scope: Scope
    visibility: str = "public"


class Source(Model):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,100}$")
    version: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=100_000)
    content_hash: str
    recorded_at: datetime
    scope: Scope
    visibility: str = "public"
    authority: list[Predicate] = Field(default_factory=list)
    revoked: bool = False

    _aware = field_validator("recorded_at")(aware)

    @model_validator(mode="after")
    def hash_matches(self):
        if self.content_hash != sha256(self.text.encode()).hexdigest():
            raise ValueError("source content hash mismatch")
        return self

    @property
    def key(self) -> str:
        return f"{self.id}@{self.version}"


class Assertion(Model):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,120}$")
    subject_id: str
    predicate: Predicate
    object_id: str | None = None
    value: str | None = None
    target_service_id: str | None = None
    source_id: str
    source_version: str
    quote: str = Field(min_length=1)
    span_start: int = Field(ge=0)
    span_end: int = Field(gt=0)
    scope: Scope
    effective_from: datetime
    effective_until: datetime | None = None
    observed_at: datetime | None = None
    method: Literal["seeded", "parsed", "extracted", "mock"]
    status: Literal["approved", "proposal"] = "approved"
    supersedes: list[str] = Field(default_factory=list)

    _aware = field_validator("effective_from", "effective_until", "observed_at")(lambda v: aware(v) if v else v)

    @model_validator(mode="after")
    def check(self):
        if (self.object_id is None) == (self.value is None):
            raise ValueError("exactly one of object_id/value is required")
        if self.span_end <= self.span_start:
            raise ValueError("empty evidence span")
        if self.effective_until and self.effective_until <= self.effective_from:
            raise ValueError("invalid effective interval")
        if self.predicate == "STATUS" and self.value not in {"open", "complete"}:
            raise ValueError("unsupported task status")
        if self.predicate == "VERIFIED_CLEAR" and self.value != "verified":
            raise ValueError("verification value must be verified")
        return self

    @property
    def source_key(self) -> str:
        return f"{self.source_id}@{self.source_version}"


class Inventory(Model):
    scope: Scope
    service_id: str
    consumer_ids: list[str]
    source_key: str
    complete: bool = False


class Bundle(Model):
    entities: list[Entity] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    assertions: list[Assertion] = Field(default_factory=list)
    inventories: list[Inventory] = Field(default_factory=list)

    @property
    def revision(self) -> str:
        payload = self.model_dump(mode="json")
        for key in payload:
            payload[key] = sorted(payload[key], key=lambda row: json.dumps(row, sort_keys=True))
        return sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


class Caller(Model):
    """Trusted server-side configuration, never an MCP argument."""
    groups: frozenset[str] = frozenset({"public"})

    def can_read(self, visibility: str) -> bool:
        return visibility == "public" or visibility in self.groups
