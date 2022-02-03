from selenium import webdriver
import time
from bs4 import BeautifulSoup
import csv


# создаем переменную OPTIONS, являющуюся экземпляром класса webdriver
# через эту переменную будем использовать методы ChromeOptions, которые будут передавать
# опции, с которыми будет запускаться движок: заголовки, режим фонового запуска, отключение режима webdriver
# сначала задаем OPTIONS, потому что используем их ПОТОМ в DRIVER. OPTIONS не связаны с DRIVER напрямую
OPTIONS = webdriver.ChromeOptions()

# включаем headless-mode (фоновый запуск без открытия окна браузера)
# OPTIONS.headless = True

# отключаем режим webdriver, маскируемся под нормальный браузер
OPTIONS.add_argument("--disable-blink-features=AutomationControlled")

# передаем ложный user-agent
OPTIONS.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36', 'accept': '*/*'")

# создаем переменную DRIVER, являющуюся экземпляром класса webdriver
# через эту переменную мы будем обращаться к webdriver и вызывать методы .get и другие и передавать им аргументы
DRIVER = webdriver.Chrome(
    executable_path="D:\\Programs\\Python Projects\\petProject 1.1 w selenium\\chromedriver\\chromedriver.exe",
    options=OPTIONS
)


HOST = 'https://www.dns-shop.ru'

URL = 'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/'


# получаем код страницы по адресу url
def get_html(url):
    try:
        DRIVER.get(url)
        time.sleep(5)
        page = DRIVER.page_source
        return page
    except Exception as ex:
        print(ex)


# ищем, сколько всего страниц видеокарт сейчас есть и выводим
# find ищет элемент, в котором содержится ссылка ('href') на последнюю страницу
# в этой ссылке есть номер последней страницы
# get('href') достает эту ссылку
def last_page_search(html):
    last_page_link = BeautifulSoup(html, 'html.parser').find(
        class_='pagination-widget__page-link pagination-widget__page-link_last'
    ).get('href')
    pages = int(last_page_link[last_page_link.find('=') + 1:])
    print('Всего страниц с видеокартами: ', pages)
    print()
    return pages


# собираем все видеокарты с текущей страницы html
def get_content(html):
    items = BeautifulSoup(html, 'html.parser').find_all(
        class_='catalog-product ui-button-widget')
    video_cards = []
    for item in items:
        video_cards.append({
            'title': item.find(class_='catalog-product__name ui-link ui-link_black').get_text(strip=True),
            'link': HOST + item.find(class_='catalog-product__name ui-link ui-link_black').get('href'),
            'price': item.find(class_='product-buy__price').get_text(strip=True).replace("₽", " ")
        })
    print('На текущей странице ', len(video_cards), ' видеокарт')
    print()
    return video_cards


# записываем полученные видеокарты в csv-файл в ряд
def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Модель', 'Ссылка', 'Цена'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['price']])


cities = ['ekaterinburg']
for city in cities:
    filename = f'{city}.csv'
    # основной код программы
    time.sleep(10)
    html = get_html(url=f'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/?city=' + city)
    # запрашиваем первую страницу, чтобы взять с нее номер последней
    last_page = last_page_search(html)  # берем номер последней страницы
    v_cards = []
    for counter in range(1, last_page + 1):  # ищем видеокарты на каждой странице
        print(f'Парсинг страницы {counter} из {last_page}')
        current_url = URL + f'?city={city}' + '&p=' + str(counter)
        print(current_url)
        html = get_html(url=current_url)
        v_cards.extend(get_content(html))
    save_file(v_cards, filename)
    print('Всего видеокарт собрано: ', len(v_cards))
DRIVER.close()  # закрытие драйвера
DRIVER.quit()
