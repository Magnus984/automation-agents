import scrapy
from urllib.parse import urljoin

# ------------------Origingal code--------------------- #

# class YahooSpider(scrapy.Spider):
#     name = "reuters"
#     allowed_domains = ["www.reuters.com"]
#     start_urls = ["https://www.reuters.com/"] 

#     custom_settings = {
#         'ROBOTSTXT_OBEY': True,  # Respect robots.txt
#         'DOWNLOAD_DELAY': 2,  # Add a delay to avoid overloading the server
#         'CONCURRENT_REQUESTS': 1,  # Limit concurrent requests
#         'FEED_FORMAT': 'json',  # Save output to a JSON file
#         'FEED_URI': 'output.json',  # Output file name
#     }

#     def parse(self, response):
#         # Extract all links from the page
#         all_links = response.css('a::attr(href)').getall()
#         print(all_links)
#         # Filter and follow valid links
#         for each_link in all_links:
#             if each_link and not each_link.startswith(('javascript:', 'mailto:', 'tel:')):  # Skip invalid links
#                 yield response.follow(each_link, self.parse_page)

#     def parse_page(self, response):
#         # Extract text content from the page
#         text = ' '.join(response.css('body :not(script):not(style)::text').getall()).strip()
#         text = ' '.join(text.split())  # Clean the text (remove extra spaces)



#         # Yield the extracted data
#         yield {
#             'url': response.url,
#             'text': text,
#         }


# spiders/dynamic_spider.py
# spiders/dynamic_spider.py
import scrapy
from urllib.parse import urlparse

class DynamicSpider(scrapy.Spider):
    name = "dynamic_spider"

    def __init__(self, start_url=None, *args, **kwargs):
        super(DynamicSpider, self).__init__(*args, **kwargs)
        if start_url:
            self.start_urls = [start_url]
            parsed_url = urlparse(start_url)
            self.allowed_domains = [parsed_url.netloc]  # Set allowed domain dynamically

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 1,
        'LOG_LEVEL': 'ERROR',  
    }

    def parse(self, response):
        # Extract all links from the page
        all_links = response.css('a::attr(href)').getall()
        for each_link in all_links:
            if each_link and not each_link.startswith(('javascript:', 'mailto:', 'tel:')):
                yield response.follow(each_link, self.parse_page)

    def parse_page(self, response):
        # Extract text content from the page
        text = ' '.join(response.css('body :not(script):not(style)::text').getall()).strip()
        text = ' '.join(text.split())  # Clean the text (remove extra spaces)

    
        yield {
            'url': response.url,
            'text': text,
        }