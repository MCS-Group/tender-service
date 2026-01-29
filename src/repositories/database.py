from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any, List
from sqlalchemy.orm import Session

class DatabaseRepository(ABC):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @abstractmethod
    def get_by_id(self, record_id: int) -> Any:
        pass

    @abstractmethod
    def get_all(self) -> List[Any]:
        pass

    @abstractmethod
    def create(self, obj_in: BaseModel) -> Any:
        pass

    @abstractmethod
    def update(self, record_id: int, obj_in: BaseModel) -> Any:
        pass

    @abstractmethod
    def delete(self, record_id: int) -> None:
        pass