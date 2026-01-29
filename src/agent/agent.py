from abc import ABC, abstractmethod
from pydantic import BaseModel
from pydantic_ai import BinaryContent
from typing import Any, Union, List
from src.logger import logger


# Define an abstract base class for sentiment analysis agents
class TenderCategoryAnalysisAgent(ABC):
    @abstractmethod
    async def analyze_tender(self, input_data: BaseModel | List[BinaryContent]):
        pass

    @abstractmethod
    async def analyze_tender_batch(self, input_data: List[BaseModel]):
        pass

class AgentProcessor:
    def __init__(self, agent: Union[TenderCategoryAnalysisAgent, Any]):
        self.agent = agent
        logger.info(f"AgentProcessor initialized with agent: {type(agent).__name__}")

    async def process(self, input_data: BaseModel | List[BinaryContent]):
        logger.debug(f"Processing single tender with {type(self.agent).__name__}")
        result = await self.agent.analyze_tender(input_data)
        logger.debug(f"Tender processing completed")
        return result
    
    async def process_batch(self, input_data: List[BaseModel]):
        logger.info(f"Processing batch of {len(input_data)} tenders")
        result = await self.agent.analyze_tender_batch(input_data)
        logger.info(f"Batch processing completed")
        return result
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.process(*args, **kwds)
    