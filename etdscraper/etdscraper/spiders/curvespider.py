import scrapy
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin
import requests
import hashlib
import time
import json

class CurvespiderSpider(scrapy.Spider):
    name = 'curvespider'
    allowed_domains = ['curve.carleton.ca']
    start_urls = ['https://curve.carleton.ca/167299e9-53e6-48d7-a28d-8af2f87719ec']
    
    def parse_single_page(self, response):
        url = 'https://curve.carleton.ca/87520c16-49cf-4e05-a4f7-58587e94936a'
        yield scrapy.Request(url=url, callback=self.parse_thesis_page)

    def parse_all_pages(self, response):
        for href in response.css('div.view-content a::attr(href)').getall():
            url = urljoin(response.url, href)
            yield scrapy.Request(url=url, callback=self.parse_thesis_page)

        # Follow the "Next" link and scrape thesis metadata from the next page
        next_page_url = response.css('li.pager-next a::attr(href)').get()
        if next_page_url:
            next_page_url = urljoin(response.url, next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse(self, response):
        with open('modified_urls.json', 'r') as f:
            data = json.load(f)
        for item in data['urls']:
            url = item['curve_url']
            if not url.startswith('http'):
                url = 'https://' + url
            yield scrapy.Request(url=url, callback=self.parse_thesis_page)

    #TODO: check this method its probably redundent at this point
    def parse_page(self, response):
        # Parse each thesis on the page
        thesis_links = response.css('div.view-content a::attr(href)').getall()
        
        for link in thesis_links:
            yield scrapy.Request(link, callback=self.parse_thesis_page)
    
    def parse_thesis_page(self, response):
        time.sleep(0.2)
        title = response.css('meta[property="og:title"]::attr(content)').get()
        creator = response.css('meta[name="dcterms.creator"]::attr(content)').get()
        date = response.css('meta[name="citation_publication_date"]::attr(content)').get()
        language_full = response.css('meta[name="dcterms.language"]::attr(content)').get()
        language = language_full.split(':')[0].strip()
        publisher = response.css('meta[name="dcterms.publisher"]::attr(content)').get()
        thesis_degree_level = response.css('.field-name-thesis-degree-level .field-item::text').get().strip()
        subject = response.css('.field-name-dcterms-subject .field-item::text').getall()
        thesis_degree_discipline = response.css('section.field-name-thesis-degree-discipline div.field-item::text').get().strip()
        abstract = response.css('meta[name="citation_abstract"]::attr(content)').get()
        contributor = response.css('section.field-name-dcterms-contributor div.double-field-second::text').getall()
        curve_url = response.css('meta[name="dcterms.identifier"]::attr(content)').get()
        doi = response.css('div.field-item a[href^="https://doi.org/"]::text').get()
        degree_name = response.css('.field-name-thesis-degree-name .double-field-first::text').get().strip()
        degree_abbr = response.css('.field-name-thesis-degree-name .double-field-second::text').get().strip()
        pdf_url = response.css('meta[name="citation_pdf_url"]::attr(content)').get()
        zip_url = response.css("span.file a::attr(href)").get()
        pdf_response = None
        zip_response = None
        if pdf_url != None:
            pdf_response = requests.get(pdf_url)
            if pdf_response.status_code == 200:
                pdf_md5_hash = hashlib.md5(pdf_response.content).hexdigest()
            else:
                print('Could not access pdf')
        if zip_url != None:
            zip_response = requests.get(zip_url)
            if zip_response.status_code == 200:
                zip_md5_hash = hashlib.md5(zip_response.content).hexdigest()
            else:
                print('Could not access zip')
    
        if zip_url or zip_response == None:
            zip_url = []
            zip_md5_hash = []


        data = {
            "identifier": doi,
            "curve_url": curve_url,
            "title": title,
            "creator": creator,
            "date": date,
            "language": language,
            "publisher": publisher,
            "thesis_degree_level": thesis_degree_level,
            "subject": subject,
            "thesis_degree_disc": thesis_degree_discipline,
            "abstract": abstract,
            "contributor": contributor,
            "thesis_degree_name": f"{degree_name} ({degree_abbr})",
            "pdf_url": pdf_url,
            "zip_url": zip_url,
            "pdf_md5_hash": pdf_md5_hash,
            "zip_md5_hash": zip_md5_hash,

         }
        yield data

