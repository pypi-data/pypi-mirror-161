import enum
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from dotenv import dotenv_values
from pydantic import (
    BaseModel,
    DirectoryPath,
    Field,
    PositiveInt,
    confloat,
    conint,
    validator,
)

# from servicefoundry.internal.template.util import validate_schema
# TODO (chiragjn): Add support for units - memory, duration, etc


class Base(BaseModel):
    class Config:
        anystr_strip_whitespace = True
        validate_all = True
        extra = "ignore"
        allow_mutation = True
        use_enum_values = True
        validate_assignment = True
        allow_population_by_field_name = True

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model) -> None:
            schema.get("properties", {}).pop("yaml_raw_", None)
            schema.get("properties", {}).pop("yaml_path_", None)

    def to_service_def(self, **kwargs) -> Dict[str, Any]:
        # TODO (chiragjn): This should call `to_service_def` on members recursively?
        return self.dict(by_alias=False)


class CPU(Base):
    required: Optional[Union[PositiveInt, confloat(ge=0.001)]]
    limit: Optional[Union[PositiveInt, confloat(ge=0.001)]]


class Memory(Base):
    required: Optional[PositiveInt]
    limit: Optional[PositiveInt]


class GPU(Base):
    limit: PositiveInt


class NameValuePair(Base):
    name: str
    value: str


class PortProtocol(str, enum.Enum):
    TCP = "TCP"
    UDP = "UDP"


PortValueType = conint(gt=0, lt=65536)


class Port(Base):
    containerPort: PortValueType = Field(..., alias="container_port")
    protocol: PortProtocol = PortProtocol.TCP

    # host_ip: Optional[str] = None
    # host_port: Optional[
    #     Union[PortValueType, Tuple[PortValueType, PortValueType]]
    # ] = None

    @classmethod
    def from_str(cls, value: str) -> "Port":
        # TODO: allow str to represent ranges and return list
        if "/" in value:
            port, protocol = value.split("/", 1)
        else:
            port, protocol = value, PortProtocol.TCP
        return cls(containerPort=int(port), protocol=PortProtocol(protocol))

    def to_str(self) -> str:
        return f"{self.containerPort}/{self.protocol}"

    @classmethod
    def parse_obj(cls, obj: Any):
        if isinstance(obj, int):
            return cls.from_str(str(obj))
        elif isinstance(obj, str):
            return cls.from_str(obj)
        return super().parse_obj(obj)


class HttpGet(Base):
    path: str
    port: PortValueType
    httpHeaders: List[NameValuePair] = Field(default_factory=list, alias="headers")


class Probe(Base):
    exec: Optional[Union[str, List[str]]] = Field(default=None)
    httpGet: Optional[HttpGet] = Field(default=None, alias="http_get")
    tcpSocket: Optional[PortValueType] = Field(default=None, alias="tcp_socket")
    initialDelaySeconds: PositiveInt = Field(default=1, alias="initial_delay")
    periodSeconds: PositiveInt = Field(default=10, alias="period")
    timeoutSeconds: PositiveInt = Field(default=10, alias="timeout")
    successThreshold: PositiveInt = Field(default=1, alias="success_threshold")
    failureThreshold: PositiveInt = Field(default=3, alias="failure_threshold")

    def __init__(self, **data: Any):
        super().__init__(**data)
        fields = ["exec", "httpGet", "tcpSocket"]
        provided = sum([getattr(self, f, None) is not None for f in fields])
        if provided != 1:
            raise ValueError(
                f"One (and only one) of the following is allowed while defining a probe: {fields}"
            )

    def to_service_def(self) -> Dict[str, Any]:
        dct = self.dict(by_alias=False, exclude_unset=True)
        if self.tcpSocket:
            dct["tcpSocket"] = {"port": self.tcpSocket}
        return dct


def _parse_and_gather_env(
    env_sources: List[Union[Path, Dict[str, str]]], context_path: Optional[Path] = None
) -> List[NameValuePair]:
    env_mapping: Dict[str, str] = {}
    for env_source in env_sources:
        if isinstance(env_source, (str, Path)):
            if context_path:
                env_source = os.path.abspath(os.path.join(context_path, env_source))
            env_mapping.update(
                dotenv_values(dotenv_path=env_source, encoding="utf-8-sig")
            )
        elif isinstance(env_source, dict):
            nv = NameValuePair.parse_obj(env_source)
            env_mapping[str(nv.name)] = str(nv.value)
        else:
            raise TypeError(f"Got Unsupported type {type(env_source)} as an env source")
    env = [NameValuePair(name=key, value=value) for key, value in env_mapping.items()]
    return env


class ServiceFoundryBuildDefinition(Base):
    build_pack: str
    options: Optional[Dict[str, str]]


class ServiceFoundryServiceDefinition(Base):
    context_path_: Optional[DirectoryPath] = Field(exclude=True, default=None)

    name: str
    cpu: CPU
    memory: Memory
    gpu: Optional[GPU]
    workspace: Optional[str] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, str] = Field(default_factory=dict)
    command: Optional[Union[str, List[str]]] = None
    args: Optional[Union[str, List[str]]] = None
    env: List[Union[str, Dict[str, str]]] = Field(default_factory=list)
    ports: List[Port] = Field(default_factory=list)
    replicas: PositiveInt = 1
    healthcheck: Optional[Probe] = Field(default=None)
    readycheck: Optional[Probe] = Field(default=None)
    inject_truefoundry_api_key: bool = True

    @validator("ports", pre=True, each_item=True)
    def parse_ports(cls, value):
        # TODO (chiragjn): Find a way to write a custom deserializer so that we don't have
        #                  to write code like this
        return Port.parse_obj(value)

    @property
    def env_parsed(self) -> List[NameValuePair]:
        # TODO (chiragjn): Find a way to write a custom deserializer so that we don't have
        #                  to write code like this
        return _parse_and_gather_env(self.env, context_path=self.context_path_)

    def to_service_def(self, *, workspace: Optional[str] = None, **kwargs):
        container = {
            "resources": {
                "cpu": self.cpu.to_service_def(),
                "memory": self.memory.to_service_def(),
            },
            "ports": [port.to_service_def() for port in self.ports],
            "env": [e.to_service_def() for e in self.env_parsed],
            "injectApiKeyInEnv": self.inject_truefoundry_api_key,
        }
        if self.gpu:
            container["resources"]["gpu"] = self.gpu.to_service_def()
        if self.command:
            container["cmd"] = self.command
        if self.args:
            container["args"] = self.args
        if self.healthcheck:
            container["livenessProbe"] = self.healthcheck.to_service_def()
        if self.readycheck:
            container["readinessProbe"] = self.readycheck.to_service_def()
        workspace = workspace or self.workspace
        dct = {
            "apiVersion": "truefoundry.io/v1",
            "kind": "Component",
            "metadata": {
                "name": self.name,
                "labels": self.labels,
                "annotations": self.annotations,
            },
            "spec": {
                "name": self.name,
                "container": container,
                "traits": {"scale": {"replicas": self.replicas}},
                "workloadType": "Server",
                "osType": "linux",
                "arch": "amd64",
                "workspace": workspace,
            },
        }
        # TODO (chiragjn): json schema validation is not passing for probe
        # validate_schema(dct, schema="schema/component_schema.json")
        return dct


class ServiceFoundryDefinition(Base):
    obj_raw_: Any = Field(exclude=True, default=None)

    version: str = "v1"
    build: Optional[ServiceFoundryBuildDefinition]
    service: ServiceFoundryServiceDefinition

    @classmethod
    def from_yaml(cls, filepath):
        with open(filepath) as f:
            obj = yaml.safe_load(f)
        # TODO (chiragjn): Find a way to eliminate this!
        obj["obj_raw_"] = obj.copy()
        obj["service"]["context_path_"] = os.path.dirname(filepath)
        instance = cls.parse_obj(obj)
        return instance

    def to_dict(self, full: bool = False) -> Dict:
        # TODO (chiragjn): This should call `to_yaml` on members recursively?
        if full:
            dct = self.dict(by_alias=True)
        else:
            # TODO (chiragjn): this is not a good approach! this will cause bugs if someone modifies the instance
            #                  and then calls to yaml but raw wouldn't have changed!
            if self.obj_raw_ is not None:
                dct = self.obj_raw_
            else:
                dct = self.dict(by_alias=True, exclude_none=True, exclude_unset=True)
        return dct

    def to_yaml(self, filepath: Union[str, Path], full: bool = False) -> None:
        dct = self.to_dict(full)
        with open(filepath, "w") as f:
            yaml.safe_dump(dct, f, sort_keys=False, indent=2)

    def to_service_def(self, **kwargs) -> Dict[str, Any]:
        # TODO (chiragjn): Move to server, this is not maintainable on cli side
        return self.service.to_service_def(**kwargs)

    def _write_definition(self, filepath):
        with open(filepath, "w") as f:
            yaml.safe_dump_all(self.to_service_def(), f, default_flow_style=False)

    def to_docker_run_command(self, image: str):
        raise NotImplementedError
