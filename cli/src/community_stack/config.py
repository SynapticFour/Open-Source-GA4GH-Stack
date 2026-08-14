from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator

from community_stack.profile_env import parse_bool

AccessLevel = Literal["public", "registered", "controlled"]
AuthProvider = Literal["ls-login", "none", "keycloak"]
WesEngine = Literal["nextflow", "snakemake", "cwl", "wdl"]
TesBackend = Literal["slurm", "local", "kubernetes"]
DeployTarget = Literal["compose", "helm", "systemd"]


class LabConfig(BaseModel):
    name: str = "Unnamed lab"
    contact: str = ""


class LsLoginConfig(BaseModel):
    client_id: str = "replace-me"
    client_secret: str = "replace-me"
    redirect_uri: str | None = None


class KeycloakConfig(BaseModel):
    """OIDC issuer (realm) base URL and confidential client for oauth2-proxy."""

    issuer_url: str = "http://keycloak:8080/realms/master"
    client_id: str = "replace-me"
    client_secret: str = "replace-me"
    redirect_uri: str | None = None


class AuthConfig(BaseModel):
    provider: AuthProvider = "none"
    ls_login: LsLoginConfig | None = None
    keycloak: KeycloakConfig | None = None


class BeaconServiceConfig(BaseModel):
    enabled: bool = True
    access_level: AccessLevel = "public"
    dataset_name: str = "Demo dataset"


class WesServiceConfig(BaseModel):
    enabled: bool = False
    engine: WesEngine = "nextflow"


class SlurmConfig(BaseModel):
    partition: str = "short"


class TesServiceConfig(BaseModel):
    enabled: bool = False
    backend: TesBackend = "local"
    slurm: SlurmConfig = Field(default_factory=SlurmConfig)


class DrsServiceConfig(BaseModel):
    enabled: bool = False
    external_url: str | None = None


class ServicesConfig(BaseModel):
    beacon: BeaconServiceConfig = Field(default_factory=BeaconServiceConfig)
    wes: WesServiceConfig = Field(default_factory=WesServiceConfig)
    tes: TesServiceConfig = Field(default_factory=TesServiceConfig)
    drs: DrsServiceConfig = Field(default_factory=DrsServiceConfig)


class DeployConfig(BaseModel):
    target: DeployTarget = "compose"
    host: str = "localhost"
    tls: bool = False


class StackConfig(BaseModel):
    lab: LabConfig = Field(default_factory=LabConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    services: ServicesConfig = Field(default_factory=ServicesConfig)
    deploy: DeployConfig = Field(default_factory=DeployConfig)

    @field_validator("services", mode="before")
    @classmethod
    def _coerce_services(cls, v: Any) -> Any:
        return v or {}

    @classmethod
    def from_yaml(cls, path: str | Path) -> StackConfig:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        return cls.model_validate(raw)


def merge_profile_env(config: StackConfig, profile: dict[str, str]) -> StackConfig:
    """Apply simple PROFILE_OVERRIDES from a parsed .env profile."""
    data = config.model_dump()

    if "INCLUDE_BEACON" in profile:
        data["services"]["beacon"]["enabled"] = parse_bool(profile.get("INCLUDE_BEACON"))
    if "INCLUDE_WES" in profile:
        data["services"]["wes"]["enabled"] = parse_bool(profile.get("INCLUDE_WES"))
    if "INCLUDE_TES" in profile:
        data["services"]["tes"]["enabled"] = parse_bool(profile.get("INCLUDE_TES"))
    if "INCLUDE_DRS" in profile:
        data["services"]["drs"]["enabled"] = parse_bool(profile.get("INCLUDE_DRS"))

    if host := profile.get("HOST"):
        data["deploy"]["host"] = host
    if "TLS" in profile:
        data["deploy"]["tls"] = parse_bool(profile.get("TLS"))

    return StackConfig.model_validate(data)
