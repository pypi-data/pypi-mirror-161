from kilroy_ws_server_py_sdk import Server

from kilroy_module_server_py_sdk.controller import ModuleController
from kilroy_module_server_py_sdk.face import Face


class ModuleServer(Server):
    def __init__(self, face: Face, *args, **kwargs) -> None:
        super().__init__(ModuleController(face), *args, **kwargs)
