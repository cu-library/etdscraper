import scrapy
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin
import requests
import hashlib
import time
import json

#TODO: set up a way ask the user what if we want to parse single page, the repo or by json 
#TODO: check for unused method/imports
#TODO: set up a better place for json files to be stored

class HyraxSpider(scrapy.Spider):

    name = 'hyraxspider'
    allowed_domains = ['digitallibrary-test2.library.carleton.ca']
    #test_domains = ['https://127.0.0.1:3000']
    start_urls = ['https://digitallibrary-test2.library.carleton.ca/catalog?locale=en']
    #start_urls = ['http://127.0.0.1:3000/catalog?locale=en']

    def parse(self, response):
        
        with open('modified_urls.json', 'r') as f:
            data = json.load(f)
        for item in data['urls']:
            url = item['hyrax_url']
            if not url.startswith('http'):
                url = 'https://' + url
            yield scrapy.Request(url=url, callback=self.parse_meta_data) 

    def parse_all_pages(self, response):
        for li in response.css('li.document'):
            if 'Thesis' in li.css('dt[data-solr-field-name="resource_type_tesim"] + dd a::text').get():
                link = response.urljoin(li.css('h3.search-result-title a::attr(href)').get())
              
                yield scrapy.Request(url=url, callback=self.parse_meta_data)

        next_page_url = response.css('ul.pagination li a[rel="next"]::attr(href)').get()
        if next_page_url:   
            next_page_url = response.urljoin(next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse_all_pages)

    def parse_single_page(self, response):
        #TODO redundent method for now remove this if we dont have user input. 
        #url = 'http://127.0.0.1:3000/concern/etds/fb4948403?locale=en'
        url = 'http://127.0.0.1:3000/concern/etds/t435gc97w?locale=en'
        #url = 'http://127.0.0.1:3000/concern/etds/rx913p88g?locale=en'
        yield scrapy.Request(url=url, callback=self.parse_meta_data)

    def parse_meta_data(self, response):
        title = response.css('div.work-title-wrapper h1::text').get()
        creator = response.css('dl.work-show dt:contains("Creator") + dd a::text').get().strip()
        date_created = response.css('li.attribute-date_created::text').get()
        language = response.css('ul.tabular li.attribute-language a::text').get()
        publisher = response.css('dl.work-show dt:contains("Publisher") + dd a::text').get().strip()
        thesis_degree_level = response.css('dl.work-show dt:contains("Thesis Degree Level") + dd a::text').get().strip()

        subjects = []
        for li in response.css('ul.tabular li.attribute-subject'):
            subject = li.css('a::text').get()
            subjects.append(subject)

        thesis_degree_discipline = response.css("dt:contains('Thesis Degree Discipline') + dd a::text").get()
        abstract = response.css("dt:contains('Abstract') + dd p::text").get()
        contributor = response.css("li.attribute-contributor span[itemprop='name'] a::text").get()
        degree_text = response.css("li.attribute-degree a::text").get()
        
        doi = response.css("li.attribute-identifier a::attr(href)").get()
        hyrax_url = response.url

        download_links = response.css('a#file_download::attr(href)').getall() 
        pdf_url = None
        zip_url = None
        pdf_md5_hash = None
        zip_md5_hash = None

        for links in set(download_links):
            response = requests.head(urljoin(hyrax_url, links))
            content_type = response.headers.get('content-type')

            if 'pdf' in content_type:
                if response.status_code == 200:
                    pdf_url = urljoin(hyrax_url, links)
                    pdf_response = requests.get(pdf_url)
                    pdf_md5_hash = hashlib.md5(pdf_response.content).hexdigest()
            elif 'zip' in content_type:
                if response.status_code == 200:
                    zip_url = urljoin(hyrax_url, links)
                    zip_response = requests.get(zip_url)
                    zip_md5_hash = hashlib.md5(zip_response.content).hexdigest()       
        
        
        if subjects == None:
            subjects = []
        
        if contributor == None:
            contributor = []

        data = {
            "identifier": doi,
            "hyrax_url": hyrax_url,
            "title": title,
            "creator": creator,
            "date": date_created,
            "language": language,
            "publisher": publisher,
            "thesis_degree_level": thesis_degree_level,
            "subject": subjects,
            "thesis_degree_disc": thesis_degree_discipline,
            "abstract": abstract,
            "contributor": contributor,
            "thesis_degree_name": degree_text,
            "pdf_url": pdf_url,
            "zip_url": zip_url,
            "pdf_md5_hash": pdf_md5_hash,
            "zip_md5_hash": zip_md5_hash,

         }
        yield data

