from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from pydantic_ai import Agent, BinaryContent

from schemas.lvl_schema import TenderOverview


class FoodCategory(str, Enum):
    TARGET_VEGETABLE = "Target Vegetable" # Хүнсний нарийн ногоо нийлүүлэх, худалдан авах тэр дундаа бууцай,кимчи байцаа, салат навч, кейл байцаа, цоохор майлз, юуцай, дууяа,розмари, яншуй, орегано, гаа, нялх соёолж, гоньд, базилик, редиск, амтат чинжүү. 
    OTHER = "Other"

    @property
    def description(self) -> str:
        descriptions = {
            FoodCategory.TARGET_VEGETABLE: "EXCLUSIVELY these 16 vegetables (бууцай/spinach, кимчи байцаа/kimchi cabbage, салат навч/salad greens, кейл байцаа/kale, цоохор майлз/choy sum, юуцай/daikon radish, розмари/rosemary, яншуй/parsley, орегано/oregano, гаа/ginger, нялх соёолж/malt sprouts, гоньд/ginseng, базилик/basil, редиск/radish, амтат чинжүү/sweet pepper, дууяа/dill). Use this category ONLY those.",
            FoodCategory.OTHER: "Any food items NOT exclusively from the 16 target vegetables above. This includes: төмс/potato, лууван/onion, сонгино/onion, манжин/carrot, сармис/garlic, томато/tomato, лоол/cucumber, and ANY mixed combinations that include non-target vegetables. Even if target vegetables are present, if there are ANY other items, it must be OTHER."
        }
        return descriptions[self]
    

class PartDetail(BaseModel):
    part_name: str = Field(..., description="Name of the part or section. E.g., Part I, Section A, etc. Should be mongolian.")
    content: str = Field(..., description="Content or description of the part. Summarize the main points mentioned in this part. Should be mongolian.")
    part_budget: Optional[float] = Field(None, description="Budget allocated for this part, if applicable.")

class FoodPartDetail(PartDetail):
    food_category_reason: str = Field(..., description="Reason for the classification. Follow these steps strictly: 1. List all vegetables found in the part. 2. Explicitly state which are on the 'Target Vegetable' list and which are not. 3. Conclude 'TARGET_VEGATABLE' only if ALL vegetables are on the target list. 4. **FINAL CHECK: Before you conclude, you MUST double-check the 'Target Vegetable' list one last time. If you see 'төмс' (potato), 'лууван' (carrot), 'сонгино' (onion), or 'сармис' (garlic), the category MUST be 'OTHER'. No exceptions.** must be in english.")
    food_category: FoodCategory = Field(..., description="Category of food for this part.")

class RequirementsDetail(BaseModel):
    # III БҮЛЭГ. ТЕХНИКИЙН ТОДОРХОЙЛОЛТ, ТАВИГДАХ ШААРДЛАГА
    main_requirements: str = Field(..., description="Extract ALL main technical specifications and requirements from section III titled 'ТЕХНИКИЙН ТОДОРХОЙЛОЛТ, ТАВИГДАХ ШААРДЛАГА'. Include quality standards, delivery requirements, packaging specifications, certification requirements, and any compliance standards mentioned. Note: БҮЛЭГ means section, not a part/lot. Be comprehensive and capture all details.")
    business_requirements: Optional[str] = Field(None, description="Extract ALL business-related requirements including payment terms, contract conditions, supplier qualifications, registration requirements, legal compliance, insurance requirements, and any other commercial terms and conditions mentioned in the document.")
    technical_requirements: Optional[str] = Field(None, description="Extract ALL technical requirements including product specifications, measurement standards, testing procedures, inspection criteria, storage conditions, transportation requirements, and any technical compliance or certification standards mentioned in the document.")
    
class PDFOverview(BaseModel):
    have_parts: bool = Field(..., description="Indicates if the PDF has multiple parts/lots (Багц).")
    parts: Optional[List[PartDetail]] = Field(None, description="List of parts/lots (Багц) in the PDF, if applicable. Do not include БҮЛЭГ (sections) as parts.")
    requirements: RequirementsDetail = Field(..., description="Technical and business requirements details, if applicable.")

class PDFFoodOverview(PDFOverview):
    parts: Optional[List[FoodPartDetail]] = Field(None, description="List of food-related parts/lots (Багц) in the PDF, if applicable.")
    is_allowed_reason: Optional[str] = Field(None, description="Detailed reason explaining the food category classification.")
    is_allowed: bool = Field(..., description="Indicates if all parts fall under the 'Target Vegetable' category. Or analize the pdf and if any part is not target vegetable then set to false.")

class PDFOverviewConfig(BaseModel):
    """Configuration for PDF Overview Extraction Agent"""
    system_prompt: str = Field(
        default="You are an expert in extracting structured data from tender documents. Extract the required information accurately and concisely.", 
        description="System prompt guiding the agent's behavior.")
    model_name: str = Field(
        default="google-gla:gemini-2.5-pro",
        title="Model Name",
        description="The name of the language model to use for generating the tender overview.",
    )

class PDFOverviewAgent:
    config: PDFOverviewConfig
    def __init__(self, config: PDFOverviewConfig):
        self.config = config
        self.agent = Agent(
            model=self.config.model_name,
            system_prompt=self.config.system_prompt,
            output_type=PDFOverview,
        )
    
    async def analyze_tender(self, input_files: list[BinaryContent]) -> PDFOverview | None:
        try:
            overview = await self.agent.run([
                *input_files
            ])
            return overview.output
        except Exception as e:
            return None
        

class PDFFoodOverviewAgent:
    config: PDFOverviewConfig
    def __init__(self, config: PDFOverviewConfig):
        self.config = config
        self.agent = Agent(
            model=self.config.model_name,
            system_prompt=self.config.system_prompt,
            output_type=PDFFoodOverview,
        )
    
    async def analyze_tender(self, input_files: list[BinaryContent]) -> PDFFoodOverview | None:
        try:
            overview = await self.agent.run([
                *input_files
            ])
            return overview.output
        except Exception as e:
            return None