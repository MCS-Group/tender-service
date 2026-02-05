import os
import sys
import json
import asyncio
import requests
import re
from typing import Optional

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser
from markdownify import markdownify as md

from src.logger import logger


#URL https://api.tender.gov.mn/api/process/300/list?endBudget=10000000000000&publishDate=2026-02-02
BASE_URL = "https://api.tender.gov.mn/api/process/300/list"
# detail url https://www.tender.gov.mn/api/get-invitation-by-document-id?tenderDocumentId=1769934209748&invitationTypeId=1
DETAIL_URL = "https://www.tender.gov.mn/api/get-invitation-by-document-id?tenderDocumentId={tenderDocumentId}&invitationTypeId=1"

# Global browser instance for reuse
_browser: Optional[Browser] = None
_playwright = None


async def get_browser() -> Browser:
    """Get or create a shared browser instance for better performance."""
    global _browser, _playwright
    if _browser is None or not _browser.is_connected():
        if _playwright is None:
            _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            args=['--disable-dev-shm-usage', '--no-sandbox']
        )
        logger.info("Created new shared browser instance")
    return _browser


async def close_browser():
    """Close the shared browser instance."""
    global _browser, _playwright
    if _browser:
        try:
            await _browser.close()
        except Exception:
            pass
        _browser = None
    if _playwright:
        try:
            await _playwright.stop()
        except Exception:
            pass
        _playwright = None
        logger.info("Closed shared browser instance")


async def get_info(url: str, output_name: str, max_retries: int = 3):
    """Fetch a job listing page using Playwright and extract jobs"""
    global _browser, _playwright
    logger.info(f"Fetching tender info from: {url}")
    
    for attempt in range(max_retries):
        context = None
        try:
            browser = await get_browser()
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            page.on("dialog", lambda dialog: dialog.accept())
            logger.debug(f"Navigating to URL: {url} (attempt {attempt + 1}/{max_retries})")
            
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            
            # Wait for specific content instead of networkidle (much faster)
            try:
                await page.wait_for_selector("button", timeout=5000)
            except:
                await page.wait_for_load_state("networkidle", timeout=10000)
            
            logger.debug("Page loaded successfully")
            # Try to find and click the "Зарлал харах" button with better error handling
            button = page.get_by_role("button", name="Зарлал харах")
            
            # Check if button exists before clicking
            button_count = await button.count()
            if button_count > 0:
                await button.wait_for(state="visible", timeout=5000)
                await button.click(timeout=5000)
                logger.debug("Clicked 'Зарлал харах' button successfully")
            else:
                # Button doesn't exist - page might already show the content or have different structure
                logger.warning(f"'Зарлал харах' button not found on page, proceeding with current content")
            raw_html = await page.content()
            html_content = BeautifulSoup(raw_html, "lxml")
            await context.close()
            return str(html_content)
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {url}: {e}")
            # Clean up context on error
            if context:
                try:
                    await context.close()
                except Exception:
                    pass
            # Reset browser if it's a connection/closed error
            if "closed" in str(e).lower() or "target" in str(e).lower():
                _browser = None
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                return ""
    return ""
        

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


async def fetch_tender_infos(publish_date: str, concurrency: int = 5) -> list:
    """Fetch tender URLs from the API for a given publish date with concurrent processing"""
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
        
        # Build list of items to process
        items_to_process = []
        for item in data:
            tender_id = item.get("tenderId")
            if tender_id:
                items_to_process.append(item)
        
        logger.info(f"Processing {len(items_to_process)} tenders concurrently (concurrency={concurrency})")
        
        # Semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrency)
        
        async def process_single_tender(item):
            """Process a single tender item"""
            async with semaphore:
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
                doc_status_code = item.get("docStatusCode")
                
                url = f"https://www.tender.gov.mn/mn/invitation/detail/{invitation_id}"
                encoded_body = ""
                detail_url = ""
                
                try:
                    html_content = await get_info(url, "tender_info_page")
                    document_id = await get_tender_document_id(html_content)
                    
                    if document_id:
                        detail_url = DETAIL_URL.format(tenderDocumentId=document_id)
                        for retry in range(3):
                            try:
                                response_detail = requests.get(detail_url, timeout=15)
                                if response_detail.status_code == 200:
                                    detail_data = response_detail.json()
                                    body = detail_data.get("data", {}).get("body", "")
                                    encoded_body = body.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
                                    markdown_content = md(encoded_body)
                                    encoded_body = markdown_content
                                    break
                            except requests.RequestException as e:
                                logger.warning(f"Retry {retry + 1}/3 failed to fetch detail for {document_id}: {e}")
                                if retry < 2:
                                    await asyncio.sleep(1 * (retry + 1))
                                else:
                                    encoded_body = ""
                except Exception as e:
                    logger.error(f"Error processing tender {tender_id}: {e}")
                
                return {
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
                    "doc_status_code": doc_status_code,
                    "official_link": f"https://www.tender.gov.mn/mn/invitation/detail/{invitation_id}",
                    "detail_url": detail_url,
                    "body": encoded_body
                }
        
        # Process all tenders concurrently
        tasks = [process_single_tender(item) for item in items_to_process]
        infos = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_infos = [info for info in infos if isinstance(info, dict)]
        
        logger.info(f"Extracted {len(valid_infos)} tender URLs for date: {publish_date}")
        return valid_infos
    except requests.RequestException as e:
        logger.error(f"Error fetching tender URLs: {e}", exc_info=True)
        return []

