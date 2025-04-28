
# Парсер Alkoteka

Scrapy-паук для сбора данных о напитках с сайта alkoteka.com с использованием Playwright для работы с JavaScript.

## Требования

- Python 3.8+
- Playwright
- Scrapy
- Scrapy-Playwright

## Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/efimov77/alkoteka_parser.git
```
```bash
cd alkoteka-parser
```
2. Установите зависимости:

```bash
pip install scrapy scrapy-playwright
playwright install
playwright install-deps
```
Настройте прокси (если нужно) в settings.py:

```python
PROXY = 'http://username:password@proxy_ip:port'
```
3. Запуск

```bash
scrapy crawl alkoteka_playwright -O output.json
```

4. Структура данных

Собранные данные сохраняются в JSON с полями:

- Название, цена, изображение, ссылка
- Маркетинговые метки
- Данные о скидках
- Характеристики товара

## Пример выходных данных

```json
{
  "timestamp": 1745755496,
  "RPC": "voda-1",
  "url": "https://alkoteka.com/product/voda-1/pere-voda-mineralnaya-prirodnaya-stolovaya-pitevaya-gazirovannaya_76057",
  "title": "Перье Вода минеральная природная столовая питьевая газированная, 0.33 Л",
  "marketing_tags": [
    "-10% онлайн"
  ],
  "brand": "Перье",
  "section": [
    "Безалкогольные напитки"
  ],
  "price_data": {
    "current": 153.0,
    "original": 169.0,
    "sale_tag": "Скидка 9%"
  },
  "stock": {
    "in_stock": true,
    "count": 0
  },
  "assets": {
    "main_image": "https://web.alkoteka.com/resize/350_500/product/9d/66/76057_image.png",
    "set_images": [],
    "view360": [],
    "video": []
  },
  "metadata": {
    "__description": "",
    "volume": "0.33 Л",
    "category": "Вода",
    "RPC": "voda-1"
  },
  "variants": 1
}
```