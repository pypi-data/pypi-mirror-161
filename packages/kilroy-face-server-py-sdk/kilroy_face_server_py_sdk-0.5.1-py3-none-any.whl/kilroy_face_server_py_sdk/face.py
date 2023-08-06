from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncIterable, Generic, Optional, Tuple
from uuid import UUID

from kilroy_face_py_shared import JSON, JSONSchema
from kilroy_face_server_py_sdk.types import StateType
from kilroy_face_server_py_sdk.utils import ConfigurableWithLoadableState


class Face(ConfigurableWithLoadableState[StateType], Generic[StateType], ABC):
    @property
    @abstractmethod
    def post_schema(self) -> JSONSchema:
        pass

    @abstractmethod
    async def post(self, post: JSON) -> UUID:
        pass

    @abstractmethod
    async def score(self, post_id: UUID) -> float:
        pass

    @abstractmethod
    def scrap(
        self,
        limit: Optional[int] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
    ) -> AsyncIterable[Tuple[UUID, JSON]]:
        pass
