from kilroy_ws_server_py_sdk import Server

from kilroy_face_server_py_sdk.controller import FaceController
from kilroy_face_server_py_sdk.face import Face


class FaceServer(Server):
    def __init__(self, face: Face, *args, **kwargs) -> None:
        super().__init__(FaceController(face), *args, **kwargs)
