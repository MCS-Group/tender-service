import os
import sys
import json
import asyncio
import requests
import re

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from markdownify import markdownify as md


from src.logger import logger


#URL https://api.tender.gov.mn/api/process/300/list?endBudget=10000000000000&publishDate=2026-02-02
BASE_URL = "https://api.tender.gov.mn/api/process/300/list"
# detail url https://www.tender.gov.mn/api/get-invitation-by-document-id?tenderDocumentId=1769934209748&invitationTypeId=1
DETAIL_URL = "https://www.tender.gov.mn/api/get-invitation-by-document-id?tenderDocumentId={tenderDocumentId}&invitationTypeId=1"

async def get_info(url: str, output_name: str, max_retries: int = 3):
    """Fetch a job listing page using Playwright and extract jobs"""
    logger.info(f"Fetching tender info from: {url}")
    
    for attempt in range(max_retries):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
                )
                page = await context.new_page()
                page.on("dialog", lambda dialog: dialog.accept())
                logger.debug(f"Navigating to URL: {url} (attempt {attempt + 1}/{max_retries})")
                
                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("networkidle", timeout=30000)
                logger.debug("Page loaded successfully")
                # Try to find and click the "Зарлал харах" button with better error handling
                button = page.get_by_role("button", name="Зарлал харах")
                
                # Check if button exists before clicking
                button_count = await button.count()
                if button_count > 0:
                    await button.wait_for(state="visible", timeout=15000)
                    await button.click(timeout=15000)
                    logger.debug("Clicked 'Зарлал харах' button successfully")
                else:
                    # Button doesn't exist - page might already show the content or have different structure
                    logger.warning(f"'Зарлал харах' button not found on page, proceeding with current content")
                raw_html = await page.content()
                html_content = BeautifulSoup(raw_html, "html.parser")
                await browser.close()
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {url}: {e}")
            if attempt < max_retries - 1:
                import asyncio
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.info(f"Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"All {max_retries} attempts failed for {url}")
                raise
    return str(html_content)
        

async def get_tender_document_id(html_content) -> str | None:
    """Extract tenderDocumentId values from raw HTML content"""
    print("Extracting tenderDocumentId from HTML content")

    tender_document_id = None
    if not html_content:
        return None

    # Match both normal JSON: "tenderDocumentId":123 and escaped payload strings: \"tenderDocumentId\":123
    matches = re.findall(r'(?:\\"|")tenderDocumentId(?:\\"|")\s*:\s*(\d+)', html_content)
    if not matches:
        matches = re.findall(r'tenderDocumentId\s*=\s*(\d+)', html_content, flags=re.IGNORECASE)
    for match in matches:
        try:
            document_id = int(match)
            return str(document_id)
        except ValueError:
            continue

    return tender_document_id


async def fetch_tender_infos(publish_date: str) -> list:
    """Fetch tender URLs from the API for a given publish date"""
    params = {
        "publishDate": publish_date
    }
    try:
        logger.info(f"Fetching tender URLs for date: {publish_date}")
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            logger.error(f"API returned non-success status for date {publish_date}: {data}")
            return []
        infos = []
        for item in data:
            tender_id = item.get("tenderId")
            tender_code = item.get("tenderCode")
            invitation_id = item.get("invitationId")
            invitation_number = item.get("invitationNumber")
            published_date = item.get("publishDate")
            tender_name = item.get("tenderName")
            total_budget = item.get("totalBudget")
            tender_type_name = item.get("tenderTypeName")
            budget_entity_name = item.get("budgetEntityName")
            fund_name = item.get("fundName")
            budget_entity_name = item.get("budgetEntityName")
            doc_status_code = item.get("docStatusCode")
            if doc_status_code == "CLOSED_STATUS":
                continue

            if tender_id:
                url = f"https://www.tender.gov.mn/mn/invitation/detail/{invitation_id}"
                html_content = await get_info(url, "tender_info_page")
                document_id = await get_tender_document_id(html_content)
                if document_id:
                    try:
                        url = DETAIL_URL.format(tenderDocumentId=document_id)

                        #body from detail url
                        response_detail = requests.get(url)
                        response_detail.raise_for_status()
                        detail_data = response_detail.json()
                        body = detail_data.get("data", {}).get("body", "")
                        #encode body
                        encoded_body = body.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
                        markdown_content = md(encoded_body)
                        encoded_body = markdown_content
                    except Exception as e:
                        body = ""
                        encoded_body = ""

                infos.append({
                    "tender_id": tender_id,
                    "tender_code": tender_code,
                    "invitation_id": invitation_id,
                    "invitation_number": invitation_number,
                    "tender_name": tender_name,
                    "total_budget": total_budget,
                    "tender_type_name": tender_type_name,
                    "publish_date": published_date,
                    "fund_name": fund_name,
                    "budget_entity_name": budget_entity_name,
                    "official_link": f"https://www.tender.gov.mn/mn/invitation/detail/{invitation_id}",
                    "detail_url": url,
                    "body": encoded_body
                })
                
        logger.info(f"Extracted {len(infos)} tender URLs for date: {publish_date}")
        return infos
    except requests.RequestException as e:
        logger.error(f"Error fetching tender URLs: {e}", exc_info=True)
        return []

