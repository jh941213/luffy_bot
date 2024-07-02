import asyncio
import nest_asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from kiwipiepy import Kiwi

# 기존 코드는 그대로 유지하고 아래 내용을 추가합니다.

nest_asyncio.apply()

async def fetch_page_content(url, selector=None):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(url)

        if selector:
            iframe_element = await page.wait_for_selector(selector)
            iframe = await iframe_element.content_frame()
            content = await iframe.evaluate("() => document.body.innerHTML")
        else:
            content = await page.content()

        await browser.close()
        return content

def extract_urls(content):
    soup = BeautifulSoup(content, 'html.parser')
    a_tags = soup.find_all('a', class_='w-full md:flex-1 md:min-w-[592px] relative')
    urls = ["https://www.aicareer.co.kr" + a['href'] for a in a_tags]
    return urls

def clean_text(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def extract_information(content):
    soup = BeautifulSoup(content, 'html.parser')

    title_div = soup.find('div', class_='text-black text-xl md:text-3xl font-bold md:font-extrabold')
    title_text = title_div.get_text(strip=True) if title_div else 'Title not found'

    company_divs = soup.find_all('div', class_='text-neutral-700 text-sm break-keep')
    company_names = [div.get_text(strip=True) for div in company_divs]

    return title_text, company_names

async def crawl_job_postings():
    main_url = "https://www.aicareer.co.kr/"
    
    content = await fetch_page_content(main_url)
    urls = extract_urls(content)
    
    job_postings = []
    
    for url in urls:
        content1 = await fetch_page_content(url)
        title_text1, company_names1 = extract_information(content1)
        
        content2 = await fetch_page_content(url, selector="iframe#iframe")
        
        job_posting = {
            "url": url,
            "title": title_text1,
            "company": company_names1[3] if len(company_names1) > 3 else 'Company not found',
            "job_title": company_names1[0] if len(company_names1) > 0 else 'Job title not found',
            "location": company_names1[2] if len(company_names1) > 2 else 'Location not found',
            "recruitment_period": company_names1[1] if len(company_names1) > 1 else 'Recruitment period not found',
            "content": clean_text(BeautifulSoup(content2, "html.parser").get_text(separator="\n"))
        }
        
        job_postings.append(job_posting)
    
    return job_postings

def get_job_postings():
    return asyncio.run(crawl_job_postings())