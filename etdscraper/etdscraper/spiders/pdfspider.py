import scrapy
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin
import requests
import hashlib
import time

class PdfspiderSpider(scrapy.Spider):
    name = 'pdfspider'
    allowed_domains = ['curve.carleton.ca']
    start_urls = ['https://curve.carleton.ca/167299e9-53e6-48d7-a28d-8af2f87719ec']

    def parse(self, response):
        # Scrape thesis metadata from the current page
        
        for href in response.css('div.view-content a::attr(href)').getall():
            url = urljoin(response.url, href)
            yield scrapy.Request(url=url, callback=self.parse_meta_data)

        # Follow the "Next" link and scrape thesis metadata from the next page
        next_page_url = response.css('li.pager-next a::attr(href)').get()
        if next_page_url:
            next_page_url = urljoin(response.url, next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_page(self, response):
        # Parse each thesis on the page
        thesis_links = response.css('div.view-content a::attr(href)').getall()
        for link in thesis_links:
            yield scrapy.Request(link, callback=self.parse_thesis_page)
    
    def parse_meta_data(self, response):
        curve_url = response.css('meta[name="dcterms.identifier"]::attr(content)').get()
        doi = response.css('div.field-item a[href^="https://doi.org/"]::text').get()
        pdf_url = response.css('meta[name="citation_pdf_url"]::attr(content)').get()
        zip_url = response.css("span.file a::attr(href)").get()
        

        data = {
            "identifier": doi,
            "curve_url": curve_url,
            "pdf_url": pdf_url,
            "zip_url": zip_url,

         }
        yield data

