# -*- coding: utf-8 -*-
import os
import sys
import time
import string
import zipfile
import logging
import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Remote
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.chrome import options

from wise_utils.spider.basespider import BaseSpider


class ReuseChrome(Remote):
    """
    用于重连已存在的浏览器，由于使用官方方法重连时，会先建一个新的浏览器，再修改 executor_url 和 session_id，多创建一个空白浏览器窗口，因此。继承并重写其start_session方法，
    """

    def __init__(self, command_executor, session_id):
        self.r_session_id = session_id
        Remote.__init__(self, command_executor=command_executor, desired_capabilities={})

    def start_session(self, capabilities, browser_profile=None):
        """
        重写start_session方法
        """
        if not isinstance(capabilities, dict):
            raise InvalidArgumentException("Capabilities must be a dictionary")
        if browser_profile:
            if "moz:firefoxOptions" in capabilities:
                capabilities["moz:firefoxOptions"]["profile"] = browser_profile.encoded
            else:
                capabilities.update({'firefox_profile': browser_profile.encoded})

        self.caps = options.Options().to_capabilities()
        self.session_id = self.r_session_id
        self.w3c = False


class SeleniumBaseSpider(BaseSpider):
    PAGE_LOAD_TIMEOUT = 180

    def __init__(self, task_name, log_level=logging.DEBUG, log_file_path=None):
        super(SeleniumBaseSpider, self).__init__(task_name=task_name, log_level=log_level, log_file_path=log_file_path)
        self.__browser_model = "local"  # 默认为本地启动

    def create_local_browser(self,
                             headless: bool = True,
                             incognito: bool = True,
                             no_picture: bool = False,
                             no_pop_ups: bool = False,
                             page_load_strategy: str = "none",
                             no_extensions: bool = False,
                             use_proxy: bool = False,
                             userdata_file_path: str = "",
                             executable_path: str = "",
                             chrome_options: webdriver.ChromeOptions = None,
                             execute_cdp_cmd: bool = False
                             ):
        """
        创建本地浏览器
        :params headless: 无头模式
        :params incognito: 无痕模式
        :params no_picture: 禁止加载图片元素
        :params no_pop_ups: 禁止弹窗
        :params page_load_strategy: 页面加载策略 可设置为三种  1 eager selenium会等待整个界面加载完成（指对html和子资源的下载与解析，不包括ajax）  2 normal 要等待整个dom树加载完成，即DOMContentLoaded这个事件完成，仅对html的内容进行下载解析 3 none 当html下载完成之后，不等待解析完成，selenium会直接返回
        :params no_extensions: 禁止使用插件
        :params use_proxy: 使用代理
        :params userdata_file_path: 保存历史和缓存（多爬虫同时使用不行）
        """
        self.__browser_model = "local"
        if sys.platform == "linux":
            # 打开虚拟窗口
            from pyvirtualdisplay import Display
            self.__display = Display(visible=False, size=(1792, 1120))
            self.__display.start()

        chrome_options = chrome_options if chrome_options else self.get_chrome_options(
            headless=headless,
            incognito=incognito,
            no_picture=no_picture,
            no_pop_ups=no_pop_ups,
            page_load_strategy=page_load_strategy,
            no_extensions=no_extensions,
            use_proxy=use_proxy,
            userdata_file_path=userdata_file_path
        )

        if executable_path:
            browser = webdriver.Chrome(executable_path=executable_path, options=chrome_options)
        else:
            # 自动下载
            from webdriver_manager.chrome import ChromeDriverManager
            browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

        if execute_cdp_cmd:
            # 隐藏浏览器特征
            with open(os.path.join(os.path.dirname(__file__), "stealth.js")) as f:
                js = f.read()
            browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js})

        browser.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)
        browser.maximize_window()
        return browser

    def create_remote_browser(self, remote_url,
                              desired_capabilities: dict = {},
                              headless: bool = True,
                              incognito: bool = True,
                              no_picture: bool = False,
                              no_pop_ups: bool = False,
                              page_load_strategy: str = "none",
                              no_extensions: bool = False,
                              use_proxy: bool = False,
                              userdata_file_path: str = "",
                              chrome_options: webdriver.ChromeOptions = None,
                              ):
        """
        创建远程浏览器: selenium grid
        :params headless: 无头模式
        :params incognito: 无痕模式
        :params no_picture: 禁止加载图片元素
        :params no_pop_ups: 禁止弹窗
        :params page_load_strategy: 页面加载策略 可设置为三种  1 eager selenium会等待整个界面加载完成（指对html和子资源的下载与解析，不包括ajax）  2 normal 要等待整个dom树加载完成，即DOMContentLoaded这个事件完成，仅对html的内容进行下载解析 3 none 当html下载完成之后，不等待解析完成，selenium会直接返回
        :params no_extensions: 禁止使用插件
        :params use_proxy: 使用代理
        :params userdata_file_path: 保存历史和缓存（多爬虫同时使用不行）
        """

        self.__browser_model = "remote"
        chrome_options = chrome_options if chrome_options else self.get_chrome_options(
            headless=headless,
            incognito=incognito,
            no_picture=no_picture,
            no_pop_ups=no_pop_ups,
            page_load_strategy=page_load_strategy,
            no_extensions=no_extensions,
            use_proxy=use_proxy,
            userdata_file_path=userdata_file_path
        )

        desired_capabilities = desired_capabilities if desired_capabilities else {
            "browserName": "chrome",
            "platformName": "linux",
            "se:recordVideo": "true",
            "se:timeZone": "Asia/Shanghai",
            "se:screenResolution": "1920x1080"
        }
        browser = webdriver.Remote(command_executor=remote_url, desired_capabilities=desired_capabilities, options=chrome_options)
        browser.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)
        browser.maximize_window()
        return browser

    def create_undetected_browser(self,
                                  chrome_version,
                                  headless: bool = True,
                                  incognito: bool = True,
                                  no_pop_ups: bool = False,
                                  page_load_strategy: str = "none",
                                  no_extensions: bool = False,
                                  userdata_file_path: str = "",
                                  chrome_options: uc.ChromeOptions = None,

                                  ):
        """通过undetected_chromedriver创建chrome，需要指定浏览器版本。可过五秒盾"""
        self.__browser_model = "undetected"

        if sys.platform == "linux":
            # 打开虚拟窗口
            from pyvirtualdisplay import Display
            self.__display = Display(visible=False, size=(1792, 1120))
            self.__display.start()

        from multiprocessing import freeze_support
        freeze_support()

        chrome_options = chrome_options if chrome_options else self.get_undetected_chrome_options(
            headless=headless,
            incognito=incognito,
            no_pop_ups=no_pop_ups,
            page_load_strategy=page_load_strategy,
            no_extensions=no_extensions,
            userdata_file_path=userdata_file_path
        )
        browser = uc.Chrome(options=chrome_options, version_main=chrome_version)

        browser.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)
        browser.maximize_window()
        return browser

    @staticmethod
    def reconnect_existed_browser(executor_url, session_id):
        """
        重新连接一个已经存在的浏览器
        :params executor_url: browser.command_executor._url
        :params session_id: browser.session_id
        """
        return ReuseChrome(command_executor=executor_url, session_id=session_id)

    def get_chrome_options(self,
                           headless: bool = True,
                           incognito: bool = True,
                           no_picture: bool = False,
                           no_pop_ups: bool = False,
                           page_load_strategy: str = "none",
                           no_extensions: bool = False,
                           use_proxy: bool = False,
                           userdata_file_path: str = "",
                           ):
        """获取chrome配置信息"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("lang=zh_CN.UTF-8")  # 设置中文
        # chrome_options.add_argument(f"user-agent={self.get_random_ua()}")  # 更换头部
        chrome_options.add_argument("--no-sandbox")  # root
        chrome_options.add_argument("--disable-gpu")  # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument("--hide-scrollbars")  # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument("--disable-infobars")  # 关闭提示
        chrome_options.add_argument("--disable-dev-shm-usage")  # 修复选项卡崩溃
        chrome_options.add_argument("--ignore-certificate-errors")  # 忽略验证：您的连接不是私密连接
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 取消chrome受自动控制提示
        # chrome_options.add_argument("–single-process")  # 单进程运行Google Chrome
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        if no_extensions:
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_experimental_option("useAutomationExtension", False)

        if no_picture:
            chrome_options.add_argument("blink-settings=imagesEnabled=false")

        if no_pop_ups:
            # 禁止弹窗加入
            prefs = {
                "profile.default_content_setting_values":
                    {
                        "notifications": 2
                    }
            }
        else:
            prefs = dict()
        prefs["credentials_enable_service"] = False
        prefs["profile.password_manager_enabled"] = False
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.set_capability("PageloadStrategy", page_load_strategy)

        if use_proxy:
            # 无头模式，无痕模式 不支持使用扩展
            headless = False
            incognito = False
            use_userdata = False
            # 获取代理
            proxy_dict = self.get_proxy_ip()
            if proxy_dict.get("username", None) is not None:
                # 创建插件
                plugin_path = self.__create_proxyauth_extension(proxy_host=proxy_dict["ip"], proxy_port=proxy_dict["port"], proxy_username=proxy_dict["username"], proxy_password=proxy_dict["password"])
                chrome_options.add_extension(plugin_path)
            else:
                # 代理不需要账号密码
                chrome_options.add_argument(f"--proxy-server=http://{proxy_dict['ip']}:{proxy_dict['port']}")

        if incognito:
            # 无痕
            chrome_options.add_argument("--incognito")

        if headless:
            # 无头
            chrome_options.add_argument("--headless")

        if userdata_file_path:
            chrome_options.add_argument(f"--user-data-dir={userdata_file_path}")
        return chrome_options

    @staticmethod
    def get_undetected_chrome_options(
            headless: bool = True,
            incognito: bool = True,
            no_pop_ups: bool = False,
            page_load_strategy: str = "none",
            no_extensions: bool = False,
            userdata_file_path: str = "",
    ):
        """获取undetected_chrome_options"""
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--disable-gpu")  # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument("--hide-scrollbars")  # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument("--disable-infobars")  # 关闭提示
        chrome_options.add_argument("--disable-dev-shm-usage")  # 修复选项卡崩溃
        chrome_options.add_argument("--ignore-certificate-errors")  # 忽略验证：您的连接不是私密连接

        if no_extensions:
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_experimental_option("useAutomationExtension", False)

        if no_pop_ups:
            # 禁止弹窗加入
            prefs = {
                "profile.default_content_setting_values":
                    {
                        "notifications": 2
                    }
            }
        else:
            prefs = dict()
        prefs["credentials_enable_service"] = False
        prefs["profile.password_manager_enabled"] = False
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.set_capability("PageloadStrategy", page_load_strategy)

        if incognito:
            # 无痕
            chrome_options.add_argument("--incognito")

        if headless:
            # 无头
            chrome_options.add_argument("--headless")

        if userdata_file_path:
            chrome_options.add_argument(f"--user-data-dir={userdata_file_path}")
        return chrome_options

    def clear_and_send_keys(self, browser, by: str, value: str, msg):
        """
        点击并发送
        每次都获取是因为有时旧的元素定位不到会报错，所以每次都重新获取元素并完成相应操作
        :param browser: 浏览器对象
        :param by: 通过什么方式定位，如： id，xpath，css_selector
        :param value: 定位的规则
        :param msg: 需要输入的值
        :return:
        """
        by = by.lower()
        self.__get_element(browser, by, value).clear()
        time.sleep(0.1)
        self.__get_element(browser, by, value).send_keys(msg)
        time.sleep(0.3)
        return True

    def find_element(self, browser, by, value):
        """获取元素"""
        return self.__get_element(browser, by, value)

    def find_element_by_xpath(self, browser, value: str):
        """通过xpath获取元素"""
        return self.__get_element(browser, "xpath", value)

    def find_element_by_id(self, browser, value: str):
        """通过id获取元素"""
        return self.__get_element(browser, "id", value)

    def find_elements(self, browser, by, value):
        """获取元素"""
        return self.__get_elements(browser, by, value)

    def find_elements_by_xpath(self, browser, value: str):
        """通过xpath获取元素"""
        return self.__get_elements(browser, "xpath", value)

    def find_elements_by_id(self, browser, value: str):
        """通过id获取元素"""
        return self.__get_elements(browser, "id", value)

    def wait_clickable_element(self, browser, by, value: str, wait=10):
        """等待可点击的元素"""
        if by == 'id':
            return self.wait_clickable_element_by_id(browser, value, wait)
        elif by == 'xpath':
            return self.wait_clickable_element_by_xpath(browser, value, wait)
        return None

    @staticmethod
    def wait_clickable_element_by_xpath(browser, value: str, wait=10):
        """等待可点击的元素"""
        return WebDriverWait(browser, wait, 0.5).until(EC.element_to_be_clickable((By.XPATH, value)))

    @staticmethod
    def wait_clickable_element_by_id(browser, value: str, wait=10):
        """等待可点击的元素"""
        return WebDriverWait(browser, wait, 0.5).until(EC.element_to_be_clickable((By.ID, value)))

    def wait_located_element(self, browser, by, value: str, wait=10):
        """等待元素"""
        if by == 'id':
            return self.wait_located_element_by_id(browser, value, wait)
        elif by == 'xpath':
            return self.wait_located_element_by_xpath(browser, value, wait)
        return None

    @staticmethod
    def wait_located_element_by_xpath(browser, value: str, wait=10):
        """等待元素"""
        return WebDriverWait(browser, wait, 0.5).until(EC.presence_of_element_located((By.XPATH, value)))

    @staticmethod
    def wait_located_element_by_id(browser, value: str, wait=10):
        """等待元素"""
        return WebDriverWait(browser, wait, 0.5).until(EC.presence_of_element_located((By.ID, value)))

    def wait_text_to_be_present(self, browser, by, value: str, text, wait=10):
        """等待元素"""
        if by == 'id':
            return self.wait_text_to_be_present_by_id(browser, value, text, wait)
        elif by == 'xpath':
            return self.wait_text_to_be_present_by_xpath(browser, value, text, wait)
        return None

    @staticmethod
    def wait_text_to_be_present_by_xpath(browser, value: str, text: str, wait=10):
        """等待文字"""
        return WebDriverWait(browser, wait, 0.5).until(EC.text_to_be_present_in_element((By.XPATH, value), text_=text))

    @staticmethod
    def wait_text_to_be_present_by_id(browser, value: str, text: str, wait=10):
        """等待文字"""
        return WebDriverWait(browser, wait, 0.5).until(EC.text_to_be_present_in_element((By.ID, value), text_=text))

    def wait_ele_to_be_selected(self, browser, by, value: str, wait=10):
        """等待选择框"""
        if by == 'id':
            return self.wait_ele_to_be_selected_by_id(browser, value, wait)
        elif by == 'xpath':
            return self.wait_ele_to_be_selected_by_xpath(browser, value, wait)
        return None

    def wait_ele_to_be_selected_by_id(self, browser, value: str, wait=10):
        """等待选择框"""
        return Select(self.wait_clickable_element_by_id(browser, value, wait))

    def wait_ele_to_be_selected_by_xpath(self, browser, value: str, wait=10):
        """等待选择框"""
        return Select(self.wait_clickable_element_by_xpath(browser, value, wait))

    @staticmethod
    def wait_alert_element(browser, wait=10):
        """等待弹窗"""
        return WebDriverWait(browser, wait, 0.5).until(EC.alert_is_present())

    def click_by_js(self, browser, by, value):
        """通过js点击"""
        by = by.lower()
        ele = self.__get_element(browser, by, value)
        browser.execute_script("arguments[0].click();", ele)
        time.sleep(0.5)
        return True

    def scroll_to_ele(self, browser, by, value):
        """滚动到某个元素的位置"""
        ele = self.__get_element(browser, by, value)
        js4 = "arguments[0].scrollIntoView();"
        browser.execute_script(js4, ele)
        return True

    def __get_element(self, browser, by, value):
        """通过不同的方式查找界面元素"""
        element = None
        by = by.lower()
        if by == "id":
            element = browser.find_element(by=By.ID, value=value)
        elif by == "name":
            element = browser.find_element(by=By.NAME, value=value)
        elif by == "xpath":
            element = browser.find_element(by=By.XPATH, value=value)
        elif by == "classname":
            element = browser.find_element(by=By.CLASS_NAME, value=value)
        elif by == "css":
            element = browser.find_element(by=By.CSS_SELECTOR, value=value)
        elif by == "link_text":
            element = browser.find_element(by=By.LINK_TEXT, value=value)
        else:
            self.logger.error("无对应方法，请检查")
        return element

    def __get_elements(self, browser, by, value):
        """通过不同的方式查找所有界面元素"""
        elements = []
        by = by.lower()
        if by == "id":
            elements = browser.find_elements(by=By.ID, value=value)
        elif by == "name":
            elements = browser.find_elements(by=By.NAME, value=value)
        elif by == "xpath":
            elements = browser.find_elements(by=By.XPATH, value=value)
        elif by == "classname":
            elements = browser.find_elements(by=By.CLASS_NAME, value=value)
        elif by == "css":
            elements = browser.find_elements(by=By.CSS_SELECTOR, value=value)
        elif by == "link_text":
            elements = browser.find_elements(by=By.LINK_TEXT, value=value)
        else:
            self.logger.error("无对应方法，请检查")
        return elements

    @staticmethod
    def get_browser_cookies(browser):
        """获取当前浏览器cookie，返回str"""
        cookie_dict = browser.get_cookies()
        cookies = ""
        for cookie in cookie_dict:
            if not cookie["name"].startswith("_"):
                cookies += cookie["name"] + "=" + cookie["value"] + ";"
        return cookies.strip(";")

    def __create_proxyauth_extension(self, proxy_host, proxy_port, proxy_username, proxy_password, scheme="http"):
        """带密码验证的扩展"""
        plugin_path = f"./proxy_auth_plugin_{self.task_name}"

        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = string.Template(
            """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                      singleProxy: {
                        scheme: "${scheme}",
                        host: "${host}",
                        port: parseInt(${port})
                      },
                      bypassList: ["foobar.com"]
                    }
                  };

            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "${username}",
                        password: "${password}"
                    }
                };
            }

            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ["blocking"]
            );
            """
        ).substitute(
            host=proxy_host,
            port=proxy_port,
            username=proxy_username,
            password=proxy_password,
            scheme=scheme,
        )
        with zipfile.ZipFile(plugin_path, "w") as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        return plugin_path

    def close_browser(self, browser):
        """
        关闭浏览器
        """
        try:
            browser.quit()
            time.sleep(0.5)
            if self.__browser_model in ["local", "undetected"] and sys.platform == "linux":
                # 关闭虚拟窗口
                self.__display.stop()
        except Exception as e:
            print(e)
        return True
