from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from simple_proxy.proxied_selenium_pool import ProxiedSeleniumPool


def get_until_title_seen(selenium_pool: ProxiedSeleniumPool,
                         url: str,
                         title: str,
                         timeout: int = 5):
    while True:
        try:
            with selenium_pool.get_session() as (proxy_info, driver):
                driver.set_page_load_timeout(60)
                driver.get(url)
                WebDriverWait(driver, timeout).until(EC.title_contains(title))

                return proxy_info, driver
        except TimeoutException:
            pass
