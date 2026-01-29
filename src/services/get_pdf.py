import os
import json
import urllib.parse
from bs4 import BeautifulSoup
from typing import List
from playwright.async_api import async_playwright
import requests

from src.logger import logger


def extract_pdf_url_from_html(content):
    """Extract job listings from HTML content"""
    tender_containers = content.find_all("div", {"class": "w-full px-0"})
    links = []
    for container in tender_containers:
        a_tags = container.find_all("a", {"class": "relative tap-highlight-transparent outline-none data-[focus-visible=true]:z-10 data-[focus-visible=true]:outline-2 data-[focus-visible=true]:outline-focus data-[focus-visible=true]:outline-offset-2 text-medium text-foreground no-underline hover:opacity-80 active:opacity-disabled transition-opacity p-3 flex items-center gap-3 rounded-lg border border-divider bg-white"}, href=True)
        for a_tag in a_tags:
            href_link = a_tag['href']
            links.append(urllib.parse.urljoin("https://www.tender.gov.mn", href_link))
    
    return links


#download pdf from download able link and save to local folder
async def download_pdf(url, output_path, max_retries=3):
    main_url ="https://api.mcs.mn/tender/stream?url="+url
    logger.info(f"Downloading PDF from: {main_url}")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(main_url, stream=True, timeout=30)
            if response.status_code == 200:
                file_size = 0
                with open(output_path, 'wb') as file:
                    # Write the content in chunks to handle large files efficiently
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                        file_size += len(chunk)
                logger.info(f"PDF downloaded successfully: {output_path} ({file_size} bytes)")
                return True
            elif response.status_code in [502, 503, 504]:
                # Server errors - retry
                logger.warning(f"Server error {response.status_code} on attempt {attempt + 1}/{max_retries}, URL: {main_url}")
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    continue
            else:
                logger.error(f"Failed to download PDF. Status code: {response.status_code}, URL: {main_url}")
                return False
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries} for {main_url}")
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep(2 ** attempt)
                continue
        except Exception as e:
            logger.error(f"Exception while downloading PDF from {main_url}: {e}", exc_info=True)
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep(2 ** attempt)
                continue
    
    logger.error(f"Failed to download PDF after {max_retries} attempts: {main_url}")
    return False


async def fetch_pdf_page(url: str, output_name: str):
    """Fetch a job listing page using Playwright and extract jobs"""
    logger.info(f"Fetching PDF links from: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        logger.debug(f"Navigating to PDF page: {url}")
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        logger.debug("PDF page loaded, parsing content")
        html_content = BeautifulSoup(await page.content(), "html.parser")
        await browser.close()
        #get tender number from url
        tender_number = url.split("/")[-1]
        links = extract_pdf_url_from_html(html_content)

        pdf_paths=[]

        for i in range(len(links)):
            pdf_url = links[i]
            tender_number_suffix = ""
            if i != 0:
                tender_number_suffix = f"_{i+1}"
            output_name_pdf = f"pdfs/tender_{tender_number}{tender_number_suffix}.pdf"

            success = await download_pdf(pdf_url, output_name_pdf)
            
            if success:
                pdf_paths.append(output_name_pdf)
            else:
                logger.warning(f"Skipping failed PDF download: {pdf_url}")
        
        logger.info(f"Successfully downloaded {len(pdf_paths)}/{len(links)} PDFs from {url}")
        return pdf_paths
    
async def download_pdfs_from_tender_page(url: str) -> List[str]:
    try:
        logger.info(f"Starting PDF download process for: {url}")
        pdf_paths = await fetch_pdf_page(url, "tender_pdf_page")
        logger.info(f"Successfully downloaded {len(pdf_paths)} PDFs from {url}")
        return pdf_paths
    except Exception as e:
        logger.error(f"Error downloading PDFs from {url}: {e}", exc_info=True)
        return []


async def main():

    url=f"https://www.tender.gov.mn/mn/invitation/detail/1766385752801"
    
    output_name="tender_pdf_page"
    links = await fetch_pdf_page(url, output_name)
    print(links)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())