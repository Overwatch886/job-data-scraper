import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

def scrape_weworkremotely_jobs(category="full-stack-programming", pages=1):
    jobs = []
    
    # We Work Remotely URL structure
    url = f"https://weworkremotely.com/categories/remote-{category}-jobs"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"Scraping We Work Remotely: {url}")
    response = requests.get(url, headers=headers)
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error: Status code {response.status_code}")
        with open('debug_wwr.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        return jobs

    soup = BeautifulSoup(response.content, 'html.parser')
    # Debug: Save the HTML to see what we're getting
    with open('debug_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"Status code: {response.status_code}")
    print(f"Page title: {soup.title.text if soup.title else 'No title'}")

     # Find job listings
    job_listings = soup.find_all('li', class_='new-listing-container')
    print(f"Found {len(job_listings)} job listings")
    
    for listing in job_listings[:15]:  # First 15 jobs
        job = extract_wwr_job_data(listing)
        if job:
            jobs.append(job)
    
    print(f"Successfully extracted {len(jobs)} jobs")
    time.sleep(2)
    return jobs

def extract_wwr_job_data(listing):
    try:
        # Find the job title
        title_elem = listing.find('h3', class_='new-listing__header__title')
        title = title_elem.text.strip() if title_elem else "Not specified"
        
        # Find company name
        company_elem = listing.find('p', class_='new-listing__company-name')
        company = company_elem.text.strip() if company_elem else "Not specified"
        
        # Find job URL
        # Find job URL - look for the link that contains "/remote-jobs/"
        job_url = ""
        all_links = listing.find_all('a')
        for link in all_links:
            href = link.get('href', '')
            if '/remote-jobs/' in href:
                job_url = f"https://weworkremotely.com{href}"
                break
        
        # Find location (headquarters)
        location_elem = listing.find('p', class_='new-listing__company-headquarters')
        location = location_elem.text.strip() if location_elem else "Remote"
        
        # Find categories (including salary info)
        categories = []
        salary = "Not specified"
        category_elems = listing.find_all('p', class_='new-listing__categories__category')
        for cat in category_elems:
            cat_text = cat.text.strip()
            categories.append(cat_text)
            if 'USD' in cat_text:
                salary = cat_text
        
        # Skip ads and sponsored content
        if 'sponsored' in title.lower() or 'bootcamp' in title.lower():
            return None
        
        return {
            'title': title,
            'company': company,
            'location': location,
            'salary': salary,
            'url': job_url,
            'categories': categories,
            'scraped_at': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error extracting job data: {e}")
        return None

if __name__ == "__main__":
    jobs = scrape_weworkremotely_jobs()
    print(f"Total jobs found: {len(jobs)}")
    
    # Save to JSON
    with open('data/jobs.json', 'w') as f:
        json.dump(jobs, f, indent=2)
    
    print("Jobs saved to data/jobs.json")
       
    # Print first few jobs as preview
    if jobs:
        print("\nFirst 3 jobs:")
        for i, job in enumerate(jobs[:3]):
            print(f"{i+1}. {job['title']} at {job['company']}")
            print(f"   Salary: {job['salary']}")
            print(f"   URL: {job['url']}")
            print()
    else:
        print("No jobs found.")