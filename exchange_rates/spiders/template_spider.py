import scrapy
from exchange_rates.items import ExchangeRateItem

class TemplateSpider(scrapy.Spider):
    name = 'template_spider'

    def __init__(self, *args, **kwargs):
        super(TemplateSpider, self).__init__(*args, **kwargs)
        
        # Load countries from text file
        with open('countries.txt') as f:
            countries = f.read().splitlines()

        start_urls = []

        # Generate the start URLs
        for i in range(len(countries)):
            for j in range(len(countries)):
                if i != j:
                    start_url = f"https://wise.com/in/currency-converter/{countries[i]}-to-{countries[j]}-rate?"
                    start_urls.append(start_url)

        self.start_urls = start_urls

    custom_settings = {
        'DOWNLOAD_DELAY': 0.25,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'PROXY_POOL_ENABLED': False,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,   
        'LOG_LEVEL': 'ERROR',
    }

    # handle_httpstatus_list = [500, 502, 503, 504, 400, 404, 429]

    def parse(self, response):
        # print(response.request.meta.get('proxy'))
        if response.status == 200:
            exchange_rate = response.css('h3.cc__source-to-target span.text-success::text').get()
            base_currency, foreign_currency = self.extract_currencies(response.url)
            yield ExchangeRateItem(base_currency=base_currency, foreign_currency=foreign_currency, exchange_rate=exchange_rate)
        else:
            base_currency, foreign_currency = self.extract_currencies(response.url)
            alt_start_url = f"https://valuta.exchange/{base_currency.upper()}-to-{foreign_currency.upper()}?"
            yield scrapy.Request(alt_start_url, callback=self.parse_alt_link,
                                  meta={'base_currency': base_currency, 'foreign_currency': foreign_currency}, dont_filter=True)

    def extract_currencies(self, url):
        currencies = url.split('/')[-1].split('-to-')
        if len(currencies) >= 2:
            return currencies[0], currencies[1].split('-')[0]
        else:
            return None, None

    def parse_alt_link(self, response): 
        if response.status == 200:
            exchange_rate = response.css('div.UpdateTime__Container-sc-136xv3i-0.gMmDCR span.UpdateTime__ExchangeRate-sc-136xv3i-1.djCdnS::text').get()
            base_currency, foreign_currency = self.extract_currencies(response.url)
            yield ExchangeRateItem(base_currency=base_currency, foreign_currency=foreign_currency, exchange_rate=exchange_rate)
        else:
            base_currency = response.meta['base_currency']
            foreign_currency = response.meta['foreign_currency']
            alt_start_url = f"https://www.xe.com/currencyconverter/convert/?Amount=1&From={base_currency.upper()}&To={foreign_currency.upper()}"
            yield scrapy.Request(alt_start_url, callback=self.parse_xe_link,
                                  meta={'base_currency': base_currency, 'foreign_currency': foreign_currency}, dont_filter=True)
            
    def parse_xe_link(self, response):
        if response.status == 200:
            mangea_rate = response.css('main.tab-box__ContentContainer-sc-28io75-3.joNDZm p.result__BigRate-sc-1bsijpp-1.dPdXSB::text').get()
            faded_digits = response.css('main.tab-box__ContentContainer-sc-28io75-3.joNDZm p.result__BigRate-sc-1bsijpp-1.dPdXSB span.faded-digits::text').get()
            
            if mangea_rate and faded_digits:
                exchange_rate = mangea_rate + faded_digits
                base_currency, foreign_currency = self.extract_currencies(response.url)
                yield ExchangeRateItem(base_currency=base_currency, foreign_currency=foreign_currency, exchange_rate=exchange_rate)

