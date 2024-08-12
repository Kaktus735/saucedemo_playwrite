import pytest
from playwright.sync_api import sync_playwright, Page, Browser, expect


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser: Browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


def test_add_to_cart(page: Page):
    username = 'standard_user'
    password = 'secret_sauce'
    firstname = 'Testname'
    lastname = 'Testlastname'
    zip_postal_code = '915000'

    # Открываем сайт
    page.goto("https://www.saucedemo.com/")

    # Логинимся
    page.fill('input[data-test="username"]', username)
    page.fill('input[data-test="password"]', password)
    page.click('input[data-test="login-button"]')

    # Добавляем товары в корзину
    page.locator('//*[@id="add-to-cart-sauce-labs-fleece-jacket"]').click()
    page.locator('//*[@id="add-to-cart-sauce-labs-backpack"]').click()
    # Проверяем количество товаров на пиктограмме корзины
    cart_badge = page.locator('.shopping_cart_badge')
    expect(cart_badge).to_have_text("2")

    # Удаляем товар из корзины
    page.locator('//*[@id="remove-sauce-labs-fleece-jacket"]').click()

    # Проверяем количество товаров на пиктограмме корзины
    cart_badge = page.locator('.shopping_cart_badge')
    expect(cart_badge).to_have_text("1")

    # Выбираем сортировку товаров от меньшего к большему (можно сделать без лишнего клика)
    page.locator('//*[@id="header_container"]/div[2]/div/span/select').click()
    page.select_option('select', value='lohi')

    # Получаем все цены товаров
    product_prices = page.locator('.inventory_item_price')
    product_prices_text = product_prices.all_inner_texts()

    # Преобразуем текстовые значения в числовые для сортировки
    product_prices_values = [float(price.replace('$', '')) for price in product_prices_text]

    # Проверяем, что список отсортирован по возрастанию
    # (expect используется для проверки состояний элементов страницы, здесь нельзя применить)
    assert product_prices_values == sorted(product_prices_values)

    # Выбираем сортировку товаров от большего к меньшему (можно сделать без лишнего клика)
    page.locator('//*[@id="header_container"]/div[2]/div/span/select').click()
    page.select_option('select', value='hilo') # step 14  "Price (high to low)"

    # Получаем все цены товаров
    product_prices = page.locator('.inventory_item_price')
    product_prices_text = product_prices.all_inner_texts()

    # Преобразуем текстовые значения в числовые для сортировки
    product_prices_values = [float(price.replace('$', '')) for price in product_prices_text]

    # Проверяем, что список отсортирован по убыванию
    # (expect используется для проверки состояний элементов страницы, здесь нельзя применить)
    assert product_prices_values == sorted(product_prices_values, reverse=True)

    # Выбираем сортировку товаров по алфавиту
    page.locator('//*[@id="header_container"]/div[2]/div/span/select').click()
    page.select_option('select', value='az')

    # Получаем все наименования товаров
    product_names = page.locator('inventory_item_name')
    product_names_text = product_names.all_inner_texts()

    # Проверяем, что список отсортирован по алфавиту
    assert product_names_text == sorted(product_names_text)

    # Выбираем сортировку товаров по алфавиту (z-a)
    page.locator('//*[@id="header_container"]/div[2]/div/span/select').click()
    page.select_option('select', value='za')

    # Получаем все наименования товаров
    product_names = page.locator('inventory_item_name')
    product_names_text = product_names.all_inner_texts()

    # Проверяем, что список отсортирован по алфавиту (обратная сортировка)
    assert product_names_text == sorted(product_names_text, reverse=True)

    # Проверяем количество товаров на пиктограмме корзины
    cart_badge = page.locator('.shopping_cart_badge')
    expect(cart_badge).to_have_text("1")

    # Оформляем покупку
    page.locator('//*[@id="item_4_title_link"]/div').click()
    page.locator('//*[@id="remove"]').click()
    page.locator('//*[@id="back-to-products"]').click()
    page.locator('//*[@id="item_0_title_link"]/div').click()
    page.locator('//*[@id="add-to-cart"]').click()
    page.locator('//*[@id="shopping_cart_container"]/a').click()
    page.locator('//*[@id="checkout"]').click()
    page.locator('//*[@id="first-name"]').fill(firstname)
    page.locator('//*[@id="last-name"]').fill(lastname)

    # Подтверждаем введенные данные
    page.locator('//*[@id="continue"]').click()

    # Проверяем наличие ошибки
    error_button = page.locator('.error-message-container.error')
    expect(error_button).to_have_text("Error: Postal Code is required")

    # Дозаполняем данные
    page.locator('//*[@id="postal-code"]').fill(zip_postal_code)
    # Подтверждаем введенные данные
    page.locator('//*[@id="continue"]').click()

    # Проверяем соответствие значения у полей: "Item total" = 9.99  "Tax" = 0.80 "Total" = 10.79
    item_total_value = page.locator('.summary_subtotal_label')
    expect(item_total_value).to_have_text('Item total: $9.99')
    tax_value = page.locator('.summary_tax_label')
    expect(tax_value).to_have_text('Tax: $0.80')
    total_value = page.locator('.summary_total_label')
    expect(total_value).to_have_text('Total: $10.79')

    # Завершаем покупку и выходим
    page.locator('//*[@id="finish"]').click()
    page.locator('//*[@id="back-to-products"]').click()
    page.locator('//*[@id="item_0_title_link"]/div').click()
    page.locator('//*[@id="react-burger-menu-btn"]').click()
    page.locator('//*[@id="inventory_sidebar_link"]').click()
    page.locator('//*[@id="react-burger-menu-btn"]').click()
    page.locator('//*[@id="logout_sidebar_link"]').click()
