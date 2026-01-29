import os
import sys
import json
import asyncio
from bs4 import BeautifulSoup
from typing import List
from playwright.async_api import async_playwright
import time
from datetime import datetime
from src.logger import logger

def extract_tender_from_html(content):
    """Extract job listings from HTML content"""
    tender_containers = content.find_all("div", {"class": "flex flex-col gap-5"})
    links = []
    for container in tender_containers:
        a_tag = container.find("a", {"class": "relative tap-highlight-transparent outline-none data-[focus-visible=true]:z-10 data-[focus-visible=true]:outline-2 data-[focus-visible=true]:outline-focus data-[focus-visible=true]:outline-offset-2 text-medium text-foreground no-underline hover:opacity-80 active:opacity-disabled transition-opacity flex mb-1 items-start"}, href=True)
        #get href link
        href_link = a_tag['href']
        # <td class="px-0 text-sm">2026-01-06 09:10</td>
        deadline_td = container.find("td", {"class": "px-0 text-sm"})  
        # get 2026-01-06 09:10 from deadline_td
        deadline = deadline_td.text
        #check deadline is not None and gt datetime now
        if deadline and datetime.strptime(deadline, "%Y-%m-%d %H:%M") > datetime.now():
            url = "https://www.tender.gov.mn/mn" + href_link
            links.append(url)
    return links

    

async def fetch_job_page(url: str, output_name: str):
    """Fetch a job listing page using Playwright and extract jobs"""
    logger.info(f"Fetching tender listings from: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        logger.debug(f"Navigating to: {url}")
        await page.goto(url)
        await page.wait_for_load_state("networkidle") 
        logger.debug("Page loaded, extracting tender links")

        html_content = BeautifulSoup(await page.content(), "html.parser")
 
        await browser.close()

        links = extract_tender_from_html(html_content)
        logger.info(f"Extracted {len(links)} tender links from {url}")
        
        return links


async def tender_links_by_date(publish_date: str) -> List[str]:
    logger.info(f"Fetching tender links for date: {publish_date}")
    url=f"https://www.tender.gov.mn/mn/invitation?page=1&perPage=100&publishDate={publish_date}"
    output_name=f"tender_page_{publish_date}"
    links = await fetch_job_page(url, output_name)
    logger.info(f"Found {len(links)} tender links for {publish_date}")
    return links

async def main():
    import asyncio
    # publish_date = time.strftime("%Y-%m-%d")
    publish_date = "2025-12-26"

    url=f"https://www.tender.gov.mn/mn/invitation?page=1&perPage=100&publishDate={publish_date}"
    
    print(f"Fetching tenders for publish date: {publish_date}")
    print(f"URL: {url}")

    output_name="tender_page"
    links = await fetch_job_page(url, output_name)
    print(links)

    #save links to json file
    with open(f"tender_links/tender_links_{publish_date}.json", "w", encoding="utf-8") as f:
        json.dump({"tender_links": links}, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())