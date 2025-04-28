import scrapy
import time
import re
from scrapy_playwright.page import PageMethod
from urllib.parse import urljoin


class AlkotekaSpider(scrapy.Spider):
    name = "alkoteka_playwright"
    start_urls = [
        'https://alkoteka.com/catalog/bezalkogolnye-napitki-1',
        'https://alkoteka.com/catalog/axioma-spirits',
        'https://alkoteka.com/catalog/slaboalkogolnye-napitki-2']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.card-product"),
                    ],
                    "playwright_include_page": True,
                    "playwright_context_kwargs": {
                        "proxy": {
                            "server": self.settings.get('PROXY'),
                            "username": "BsZOoXzLEv",
                            "password": "q4U4qLTCGk"},
                    },
                },
                callback=self.parse,
                errback=self.errback,
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]

        scroll_attempts = 0
        max_attempts = 20
        previous_count = 0
        current_count = len(response.css('div.card-product'))

        while scroll_attempts < max_attempts and previous_count != current_count:
            scroll_attempts += 1
            previous_count = current_count

            await page.evaluate("""
                window.scrollTo({
                    top: document.body.scrollHeight,
                    behavior: 'smooth'
                });
            """)
            
            try:
                await page.wait_for_function(
                    f"document.querySelectorAll('div.card-product').length > {previous_count}",
                    timeout=5000
                )
            except:
                self.logger.info("No new products loaded, waiting...")
                await page.wait_for_timeout(3000)

            html = await page.content()
            response = response.replace(body=html)
            current_count = len(response.css('div.card-product'))

        await page.close()

        products = response.css('div.card-product')
        for product in products:
            yield self.parse_product(product, response)

    def parse_product(self, product, response):
        # Основные данные
        title = product.css('h3.text--h5::text').get('').strip()
        volume = product.css('.card-product__tags label:contains("Л")::text').get('').strip()
        full_title = f"{title}, {volume}" if volume else title

        # Цены с обработкой
        price_text = product.css('p.button-count__title span::text').get('')
        price_text = price_text.replace('\xa0', '').replace(' ', '') if price_text else '0'

        current_price_text = product.css('p.button-count__title::text').get('')
        current_price_text = current_price_text.replace('\xa0', '').replace(' ', '') if current_price_text else price_text

        try:
            original_price = float(price_text) if price_text else 0
            current_price = float(re.search(r'\d+', current_price_text).group()) if current_price_text else original_price
        except (ValueError, AttributeError):
            original_price = current_price = 0
        # Маркетинговые теги
        marketing_tags = []
        discount_tag = product.css('.card-product__img-tag::text').get()
        if discount_tag:
            marketing_tags.append(discount_tag.strip())

        # Ссылки
        link = product.css('a::attr(href)').get()
        full_link = urljoin(response.url, link) if link else ''

        # Изображения
        main_image = product.css('.card-product__img-wrap img::attr(src)').get()

        # Формируем итоговый объект
        return {
            "timestamp": int(time.time()),
            "RPC": self.extract_rpc(link) if link else '',
            "url": full_link,
            "title": full_title,
            "marketing_tags": marketing_tags,
            "brand": self.extract_brand(title),
            "section": ["Безалкогольные напитки"],
            "price_data": {
                "current": current_price,
                "original": original_price,
                "sale_tag": self.get_sale_tag(current_price, original_price),
            },
            "stock": {
                "in_stock": True if current_price > 0 else False,
                "count": 0
            },
            "assets": {
                "main_image": urljoin(response.url, main_image) if main_image else '',
                "set_images": [],
                "view360": [],
                "video": []
            },
            "metadata": {
                "__description": title,
                "volume": volume,
                "category": product.css('.card-product__tags label:not(:contains("Л"))::text').get('').strip(),
                "RPC": self.extract_rpc(link) if link else ''
            },
            "variants": 1
        }

    def extract_rpc(self, url):
        match = re.search(r'product/([^/]+)/', url)
        return match.group(1) if match else ''

    def extract_brand(self, title):
        return title.split()[0] if title else ''

    def get_sale_tag(self, current, original):
        if original > 0 and current < original:
            discount = round((original - current) / original * 100)
            return f"Скидка {discount}%"
        return ""

    async def errback(self, failure):
        page = failure.request.meta.get('playwright_page')
        if page:
            await page.close()
