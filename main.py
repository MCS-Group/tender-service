import asyncio
import json
import os
from dataclasses import asdict, is_dataclass
from enum import Enum

from pydantic import BaseModel
from dotenv import load_dotenv
from pydantic_ai import BinaryContent
load_dotenv()

from src.services.get_info import get_info_from_tender_page, get_info_and_save
from src.services.get_pdf import download_pdfs_from_tender_page
from src.services.get_tenders import fetch_tender_infos
from src.logger import logger
from src.agent.agent import AgentProcessor
from schemas.lvl_schema import TenderOverview, TenderOverviewConfig, TenderOverviewAgent, dict_of_level
from schemas.pdf_schema import PDFOverview, PDFFoodOverview, PDFOverviewConfig, PDFOverviewAgent, PDFFoodOverviewAgent, FoodCategory


def _json_default(value):
    if isinstance(value, BaseModel):
        dump = getattr(value, "model_dump", None)
        if callable(dump):
            return dump()
        return value.model_dump()
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, set):
        return list(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")

async def main(output_name: str = "tender_overviews", start_date: str = "2026-01-02", end_date: str = "2026-01-02"):
    logger.info(f"Starting tender processing from {start_date} to {end_date}")
    logger.info(f"Output will be saved as: {output_name}")
    config = TenderOverviewConfig()
    agent = TenderOverviewAgent(config)
    processor = AgentProcessor(agent)
    overviews = []
    infos = []
    
    publish_dates = []
    current_date = start_date
    from datetime import datetime, timedelta
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    while current_date <= end_date_obj.strftime("%Y-%m-%d"):
        publish_dates.append(current_date)
        current_date_obj = datetime.strptime(current_date, "%Y-%m-%d") + timedelta(days=1)
        current_date = current_date_obj.strftime("%Y-%m-%d")

    logger.info(f"Processing {len(publish_dates)} dates: {publish_dates}")
    for publish_date in publish_dates:
        tender_infos = await fetch_tender_infos(publish_date)
        infos.extend(tender_infos)
        logger.info(f"Fetched {len(tender_infos)} tender infos for date: {publish_date}")
    logger.info(f"Total infos collected: {len(infos)}")
    if os.path.exists(f"tender_data/{output_name}.json"):
            with open(f"tender_data/{output_name}.json", "r", encoding="utf-8") as f:
                existing_overviews = json.load(f)
            overviews.extend(existing_overviews)
            logger.info(f"Loaded {len(existing_overviews)} existing overviews from tender_data/{output_name}.json")
    else:
        logger.info("Processing tender infos to generate overviews")
        logger.info(f"Processing {len(infos)} tender infos using AI agent")
        results = await processor.process_batch(infos)
        
        if results is None:
            logger.warning("AI agent returned None results")
            results = []
        
        if results:
            logger.info(f"Successfully processed {len(results)} tender overviews")
            for result, info in zip(results, infos):
                logger.debug(f"Matched result for tender: {result.name}")
                logger.debug(f"Official link: {info.get('official_link', '')}")
                
                # Handle None values for categories
                tender_category = result.tender_category if result.tender_category is not None else []
                tender_category_detail = result.tender_category_detail if result.tender_category_detail is not None else []
                
                overview = {
                    "name": result.name,
                    "selection_number": result.selection_number,
                    "ordering_organization": result.ordering_organization,
                    "announced_date": result.announced_date,
                    "deadline_date": result.deadline_date,
                    "official_link": info.get("official_link", ""),
                    "total_budget": result.total_budget,
                    "budget_type": result.budget_type,
                    "tender_type": dict_of_level.get(result.tender_type, result.tender_type),
                    "summary": result.summary,
                    "level1": result.tender_type,
                    "tender_category": [dict_of_level.get(t, "") for t in tender_category],
                    "level2": tender_category,
                    "tender_category_detail": [dict_of_level.get(t, "") for t in tender_category_detail],
                    "level3": tender_category_detail,
                    "body": info.get("body", "")
                }
                overviews.append(overview)

        
            #save overviews to json file
            logger.info(f"Saving {len(overviews)} overviews to tender_data/{output_name}.json")
            with open(f"tender_data/{output_name}.json", "w", encoding="utf-8") as f:
                json.dump(overviews, f, ensure_ascii=False, indent=4)
            logger.info(f"Successfully saved overviews to file")
    logger.info(f"Main processing completed. Total overviews: {len(overviews)}")
    return overviews

    
async def specific_pdf_download(overviews: list[dict], output_name: str):

    logger.info(f"Starting specific PDF download process for {len(overviews)} overviews")
    #specific categories to analize pdf
    category_list = [
        "G07",
        "S10",
        "S11",
        "S12",
        "S13",
        "S14",
        "S15",
        "S16",
    ]
    logger.debug(f"Target categories: {', '.join(category_list)}")
    filtered_overviews = [overview for overview in overviews if any(cat in overview.get("level2", []) for cat in category_list)]
    logger.info(f"Filtered overviews count for specific categories: {len(filtered_overviews)}")
    #additional filter only on G07 detail 007
    initial_count = len(filtered_overviews)
    filtered_overviews = [
        overview for overview in filtered_overviews
        if not ("G07" in overview.get("level2", []) and "G07_007" not in overview.get("level3", []))
    ]
    if len(filtered_overviews) < initial_count:
        logger.info(f"Applied G07 detail filter: removed {initial_count - len(filtered_overviews)} overviews")
    
    #save pdfs
    logger.info(f"Downloading PDFs for {len(filtered_overviews)} tenders")
    pdf_download_count = 0
    for idx, overview in enumerate(filtered_overviews, 1):
        official_link = overview.get("official_link", "")
        if not official_link:
            logger.warning(f"Tender [{idx}/{len(filtered_overviews)}] has no official link, skipping PDF download")
            continue
        logger.info(f"[{idx}/{len(filtered_overviews)}] Processing tender: {overview.get('name', 'N/A')}")
        pdf_paths = await download_pdfs_from_tender_page(official_link)
        overview["pdf_paths"] = pdf_paths
        pdf_download_count += len(pdf_paths)
        logger.info(f"Downloaded {len(pdf_paths)} PDFs for tender: {overview.get('name', '')}")
    logger.info(f"Total PDFs downloaded: {pdf_download_count}")
    #save filtered overviews with pdf paths to json file
    logger.info("Saving filtered overviews with PDF info to file")
    with open(f"tender_data/{output_name}_pdfs.json", "w", encoding="utf-8") as f:
        json.dump(filtered_overviews, f, ensure_ascii=False, indent=4)
    logger.info("Filtered overviews saved successfully")

    
    food_overviews = []
    software_overviews = []
    for overview in filtered_overviews:
        if "G07" in overview.get("level2", []):
            food_overviews.append(overview)
        else:
            software_overviews.append(overview)
    
    logger.info(f"Categorized: {len(food_overviews)} food tenders, {len(software_overviews)} software tenders")
    
    pdf_results = []

    #process food overviews
    if food_overviews:
        logger.info(f"Processing {len(food_overviews)} food tenders with AI agent")
        food_config = PDFOverviewConfig()
        food_agent = PDFFoodOverviewAgent(food_config)
        food_processor = AgentProcessor(food_agent)
        #get pdfs from overviews

        for idx, overview in enumerate(food_overviews, 1):
            logger.info(f"[{idx}/{len(food_overviews)}] Analyzing food tender: {overview.get('name', 'N/A')}")
            inputs = []
            pdf_paths = overview.get("pdf_paths", [])
            for pdf_path in pdf_paths:
                with open(pdf_path, "rb") as f:
                    pdf_content = f.read()
                inputs.append(BinaryContent(pdf_content, media_type="application/pdf"))

            food_result = await food_processor.process(inputs)
            logger.debug(f"AI analysis completed for food tender")

            if not food_result:
                logger.warning(f"No result from AI analysis for food tender: {overview.get('name', 'N/A')}")
                continue

            overview_data = {
                **overview,
                "have_parts": food_result.have_parts,
                "parts": [p.model_dump() if hasattr(p, 'model_dump') else p for p in food_result.parts] if food_result.parts else [],
                "requirements": food_result.requirements.model_dump() if hasattr(food_result.requirements, 'model_dump') else food_result.requirements,
                "main_category": "Нарийн хүнсний ногоо нийлүүлэл"
            }
            pdf_results.append(overview_data)
            logger.info(f"Successfully processed food tender with {len(food_result.parts) if food_result.parts else 0} parts")
    
    if software_overviews:
        logger.info(f"Processing {len(software_overviews)} software tenders with AI agent")
        software_config = PDFOverviewConfig()
        software_agent = PDFOverviewAgent(software_config)
        software_processor = AgentProcessor(software_agent)
        #get pdfs from overviews

        for idx, overview in enumerate(software_overviews, 1):
            logger.info(f"[{idx}/{len(software_overviews)}] Analyzing software tender: {overview.get('name', 'N/A')}")
            inputs = []
            pdf_paths = overview.get("pdf_paths", [])
            for pdf_path in pdf_paths:
                with open(pdf_path, "rb") as f:
                    pdf_content = f.read()
                inputs.append(BinaryContent(pdf_content, media_type="application/pdf"))

            software_result = await software_processor.process(inputs)
            if not software_result:
                logger.warning(f"No result from AI analysis for software tender: {overview.get('name', 'N/A')}")
                continue

            #save software results
            overview_data = {
                **overview,
                "have_parts": software_result.have_parts,
                "parts": [p.model_dump() if hasattr(p, 'model_dump') else p for p in software_result.parts] if software_result.parts else [],
                "requirements": software_result.requirements.model_dump() if hasattr(software_result.requirements, 'model_dump') else software_result.requirements,
                "main_category": "Программ, систем хөгжүүлэлт"
            }
            pdf_results.append(overview_data)
            logger.info(f"Successfully processed software tender with {len(software_result.parts) if software_result.parts else 0} parts")

    logger.info(f"PDF processing completed. Total results: {len(pdf_results)}")
    #save pdf results to json file
    logger.info(f"Saving PDF analysis results to tender_data/{output_name}.json")
    with open(f"tender_data/{output_name}.json", "w", encoding="utf-8") as f:
        json.dump(pdf_results, f, ensure_ascii=False, indent=4, default=_json_default)
    logger.info("PDF results saved successfully")

    return pdf_results
    
    
if __name__ == "__main__":
    asyncio.run(main())