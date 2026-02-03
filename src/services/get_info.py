import os
import json
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser
from typing import List, Optional
import re
from collections import Counter
import asyncio

from src.logger import logger

# Global browser instance for reuse
_browser: Optional[Browser] = None
_playwright = None


async def get_browser() -> Browser:
    """Get or create a shared browser instance for better performance."""
    global _browser, _playwright
    if _browser is None or not _browser.is_connected():
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
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None
        logger.info("Closed shared browser instance")


def clean_text(text):
    """Clean text by removing quotes and normalizing whitespace"""
    if not text:
        return ""
    text = text.replace('"', '')
    # Replace all whitespace (including non-breaking spaces) with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def safe_text(el) -> str:
    """Safely extract text from a BeautifulSoup element."""
    if el is None:
        return ""
    # get_text handles nested tags more reliably than .text
    return clean_text(el.get_text(" "))


def extract_tender_document_id(raw_html: str):
    """Best-effort extraction of tenderDocumentId from the page HTML.

    The tender.gov.mn pages are Next.js apps; IDs are often embedded inside script payloads.
    We pick the most frequent match to avoid grabbing unrelated IDs.
    """
    if not raw_html:
        return None

    # Match both normal JSON: "tenderDocumentId":123 and escaped payload strings: \"tenderDocumentId\":123
    matches = re.findall(r'(?:\\"|")tenderDocumentId(?:\\"|")\s*:\s*(\d+)', raw_html)
    if not matches:
        matches = re.findall(r'tenderDocumentId\s*=\s*(\d+)', raw_html, flags=re.IGNORECASE)
    if not matches:
        return None

    most_common, _count = Counter(matches).most_common(1)[0]
    try:
        return int(most_common)
    except ValueError:
        return None

def get_info_from_html(content):
    """Extract tender details from HTML content."""
    results = {}

    #get name h1 tag
    name_h1 = content.find("h1", {"class": "text-2xl lg:text-3xl font-bold mb-4"})
    if name_h1 is None:
        # Fallback: some pages may use a different heading structure
        name_h1 = content.find("h1")
    results["name"] = safe_text(name_h1)

    main_container = content.find("div", {"class": "p-4 md:p-6 rounded-lg bg-default-100"})
    if main_container is None:
        logger.warning("Main tender info container not found; returning partial result")
        results["details"] = []
        return results

    sub_containers = main_container.find_all(
        "div", {"class": "grid grid-cols-1 md:grid-cols-2 items-center md:gap-4"}
    )

    for container in sub_containers:
        label_div = container.find("div", {"class": "text-sm md:text-right text-default-500 font-light"})
        #label starts with a colon so i need to extract the value after the colon
        value_div = container.find_all("div", {"class": "text-sm"})
        value_node = None
        if len(value_div) > 1:
            value_node = value_div[1]
        elif len(value_div) == 1:
            value_node = value_div[0]
            
        # check if value node contains a div
        inner_div = value_node.find("div") if value_node else None
        if inner_div is not None:
            value = safe_text(inner_div)
        else:
            value = safe_text(value_node)

        label = safe_text(label_div)
        if not label:
            # Avoid crashing; keep some traceable key
            label = "unknown"

        results[label] = value

    results["details"] = []

    # find description from dailog section
    dialog_container = content.find("div", {"class": "flex flex-1 flex-col gap-3 p-10 pt-10"})
    
    # capture list entries from every ordered or unordered list in the dialog
    list_elements = dialog_container.find_all(["ol", "ul"]) if dialog_container else []
    for list_tag in list_elements:
        for li in list_tag.find_all("li"):
            detail_text = clean_text(li.get_text(" "))
            if detail_text:
                results["details"].append(detail_text)

    return results


async def get_info(url: str, output_name: str, max_retries: int = 3, browser: Optional[Browser] = None):
    """Fetch a job listing page using Playwright and extract jobs.
    
    Args:
        url: The URL to fetch
        output_name: Name for output (not used currently)
        max_retries: Number of retry attempts
        browser: Optional shared browser instance for better performance
    """
    logger.info(f"Fetching tender info from: {url}")
    
    for attempt in range(max_retries):
        try:
            # Use shared browser or create a new one
            if browser is not None:
                current_browser = browser
            else:
                current_browser = await get_browser()
            
            context = await current_browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            page.on("dialog", lambda dialog: dialog.accept())
            logger.debug(f"Navigating to URL: {url} (attempt {attempt + 1}/{max_retries})")
            
            # Use domcontentloaded instead of load for faster initial response
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            
            # Wait for specific content instead of networkidle (much faster)
            try:
                await page.wait_for_selector("div.p-4.md\\:p-6.rounded-lg.bg-default-100", timeout=10000)
            except:
                # Fallback to shorter networkidle if selector not found
                await page.wait_for_load_state("networkidle", timeout=15000)
            
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
            html_content = BeautifulSoup(raw_html, "lxml")  # lxml is faster than html.parser
            await context.close()  # Close context, not browser
            
            info = get_info_from_html(html_content)
            tender_document_id = extract_tender_document_id(raw_html)
            if tender_document_id is not None:
                info["tenderDocumentId"] = tender_document_id
            logger.debug(f"Successfully extracted info from {url}: {info.get('name', 'N/A')}")
            return info
                
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
    
async def get_info_from_tender_page(url: str):
    try:
        logger.info(f"Processing tender page: {url}")
        info = await get_info(url, "tender_info_page")
        if info:
            info["official_link"] = url
            logger.info(f"Successfully processed tender: {info.get('name', 'N/A')}")
        else:
            logger.warning(f"No info extracted from {url}")
        return info
    except Exception as e:
        logger.error(f"Error processing tender page {url}: {e}", exc_info=True)
        return {}

async def get_info_and_save(urls: List[str], output_name: str, ignore_existing: bool = False, concurrency: int = 5):
    """Fetch info from multiple URLs with concurrent processing.
    
    Args:
        urls: List of URLs to process
        output_name: Output file path
        ignore_existing: Whether to skip existing URLs
        concurrency: Number of concurrent requests (default 5)
    """
    #check if file exists
    existing_infos = []
    if ignore_existing and os.path.exists(output_name):
        with open(output_name, "r", encoding="utf-8") as f:
            existing_infos = json.load(f)
        logger.info(f"Loaded {len(existing_infos)} existing infos from {output_name}")
    all_infos = existing_infos.copy()
    existing_urls = {info.get("official_link") for info in existing_infos}
    
    # Filter URLs that need processing
    urls_to_process = [url for url in urls if url not in existing_urls]
    
    if not urls_to_process:
        logger.info("No new URLs to process")
        return all_infos
    
    logger.info(f"Processing {len(urls_to_process)} URLs with concurrency={concurrency}")
    
    # Get shared browser instance
    browser = await get_browser()
    
    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(concurrency)
    
    async def process_url(url: str):
        async with semaphore:
            try:
                info = await get_info(url, "tender_info_page", browser=browser)
                if info:
                    info["official_link"] = url
                    logger.info(f"Successfully processed: {info.get('name', 'N/A')[:50]}...")
                return info
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
                return None
    
    # Process URLs concurrently
    tasks = [process_url(url) for url in urls_to_process]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Collect successful results
    for result in results:
        if result and not isinstance(result, Exception):
            all_infos.append(result)
    
    #save all infos to json file
    with open(output_name, "w", encoding="utf-8") as f:
        json.dump(all_infos, f, ensure_ascii=False, indent=4)
    
    logger.info(f"Saved {len(all_infos)} total infos to {output_name}")
    return all_infos



async def main():

    url=f"https://www.tender.gov.mn/mn/invitation/detail/1766385743198"
    
    output_name="tender_info_page"
    info = await get_info(url, output_name)
    print(info)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())