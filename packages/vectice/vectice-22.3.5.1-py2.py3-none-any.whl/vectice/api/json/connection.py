from typing import Optional, List, Union, Dict, Any

from vectice.api.json.connection_type import ConnectionType


class ParameterInput:
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value


class ConnectionInput:
    def __init__(
        self, name: str, type: ConnectionType, parameters: Optional[Dict[str, str]] = None, description: str = ""
    ):
        self.name = name
        self.parameters: Optional[List[ParameterInput]] = (
            None if parameters is None else [ParameterInput(key, value) for key, value in parameters.items()]
        )
        self.type = type
        self.description = description


class ConnectionOutput:
    def __init__(
        self,
        id: int,
        name: str,
        type: Union[ConnectionType, str],
        workspaceId: int,
        parameters: Optional[List[Dict[str, Any]]] = None,
        description: Optional[str] = None,
        *args,
        **kwargs
    ):
        self._id = int(id)
        self._name = str(name)
        self._type = type if isinstance(type, ConnectionType) else ConnectionType[str(type)]
        self._description = "" if description is None else str(description)
        self._workspaceId = int(workspaceId)
        self._parameters = (
            []
            if parameters is None
            else [ParameterInput(parameter["key"], parameter["value"]) for parameter in parameters]
        )
        self._extra = kwargs

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def status(self) -> str:
        return str(self._extra["status"])

    @property
    def workspace_id(self) -> int:
        return self._workspaceId

    @property
    def description(self) -> str:
        return self._description

    @property
    def parameters(self) -> Dict[str, str]:
        return {p.key: p.value for p in self._parameters}
