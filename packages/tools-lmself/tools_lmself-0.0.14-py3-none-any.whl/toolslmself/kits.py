import os
import re
import time
import requests
from PIL import ImageGrab  # pip install Pillow -i https://mirrors.aliyun.com/pypi/simple
from selenium import webdriver  # pip install selenium -i https://mirrors.aliyun.com/pypi/simple
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class get_selenium:
    mobileType = [
        "Apple iPhone 3GS",
        "Apple iPhone 4",
        "Apple iPhone 5",
        "Apple iPhone 6",
        "Apple iPhone 6 Plus",
        "BlackBerry Z10",
        "BlackBerry Z30",
        "Google Nexus 4",
        "Google Nexus 5",
        "Google Nexus S",
        "HTC Evo, Touch HD, Desire HD, Desire",
        "HTC One X, EVO LTE",
        "HTC Sensation, Evo 3D",
        "LG Optimus 2X, Optimus 3D, Optimus Black",
        "LG Optimus G",
        "LG Optimus LTE, Optimus 4X HD",
        "LG Optimus One",
        "Motorola Defy, Droid, Droid X, Milestone",
        "Motorola Droid 3, Droid 4, Droid Razr, Atrix 4G, Atrix 2",
        "Motorola Droid Razr HD",
        "Nokia C5, C6, C7, N97, N8, X7",
        "Nokia Lumia 7X0, Lumia 8XX, Lumia 900, N800, N810, N900",
        "Samsung Galaxy Note 3",
        "Samsung Galaxy Note II",
        "Samsung Galaxy Note",
        "Samsung Galaxy S III, Galaxy Nexus",
        "Samsung Galaxy S, S II, W",
        "Samsung Galaxy S4",
        "Sony Xperia S, Ion",
        "Sony Xperia Sola, U",
        "Sony Xperia Z, Z1",
        "Amazon Kindle Fire HDX 7″",
        "Amazon Kindle Fire HDX 8.9″",
        "Amazon Kindle Fire (First Generation)",
        "Apple iPad 1 / 2 / iPad Mini",
        "Apple iPad 3 / 4",
        "BlackBerry PlayBook",
        "Google Nexus 10",
        "Google Nexus 7 2",
        "Google Nexus 7",
        "Motorola Xoom, Xyboard",
        "Samsung Galaxy Tab 7.7, 8.9, 10.1",
        "Samsung Galaxy Tab",
        "Notebook with touch",
        "iPhone 6"
    ]
    selenium_object = {
        'url': '',
        'title': '',
        'page_content': '',
    }

    @staticmethod
    def selenium_screenshot2pic(url, pic_name, size=(1920, 1080), pic_savepath=fr'pics', isMobile=False, mobileModel=None, showPosition=(0, 0), delay=3, log=False, chromedriverPath=r''):
        """
        selenium 浏览器截图
        :param url: 截图地址
        :param pic_name: 截图名称
        :param size: 截图大小
        :param pic_savepath: 截图保存路径
        :param isMobile: 是否手机模式访问
        :param mobileModel: 手机型号
        :param showPosition: selenium显示位置
        :param delay: 延时截图
        :param log: 显示日志
        :param chromedriverPath: chromedriver路径
        :return:
        """
        if not chromedriverPath:
            print('Please download chromedriver: https://registry.npmmirror.com/binary.html?path=chromedriver/')
            exit()
        if not os.path.exists(pic_savepath):
            os.mkdir(pic_savepath)

        printer = lambda *args, **kwargs: print(*args, **kwargs) if log else False

        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 隐藏正受到自动测试软件的控制

        if isMobile:
            if isinstance(mobileModel, int):
                mobile_emulation = {"deviceName": get_selenium.mobileType[mobileModel - 1]}
            elif isinstance(mobileModel, dict):
                mobile_emulation = mobileModel
            else:
                mobile_emulation = {
                    "deviceMetrics": {"width": size[0], "height": size[1], "pixelRatio": 3.0},  # 定义设备高宽，像素比
                    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"  # 通过UA来模拟
                }
            chrome_options.add_experimental_option('mobileEmulation', mobile_emulation)

        driver = webdriver.Chrome(options=chrome_options, service=Service(chromedriverPath))  # python新版本
        # driver = webdriver.Chrome(options=chrome_options, executable_path='../../self/20191014_selenium_getTitle/chromedriver_win32/chromedriver.exe')  # python旧版本
        driver.set_window_rect(showPosition[0], showPosition[1], size[0], size[1])  # 设置摆放位置
        # driver.maximize_window()  # 最大化浏览器
        driver.implicitly_wait(10)
        try:
            driver.get(url)
            time.sleep(delay)
            printer('selenium visiting URL ==>', url)

            # region 补充selenium_object
            try:
                get_selenium.selenium_object['url'] = driver.current_url
            except Exception as e:
                printer('url -> error:', e)
            try:
                get_selenium.selenium_object['title'] = driver.title
            except Exception as e:
                printer('title -> error:', e)
            try:
                get_selenium.selenium_object['page_content'] = driver.page_source
            except Exception as e:
                printer('page_content -> error:', e)
            # endregion

            im = ImageGrab.grab((showPosition[0] + 10, showPosition[1], size[0], size[1]))
            pic_name = re.sub(r'[\\/:*?"<>|]', '', pic_name)
            im.save(fr"{pic_savepath}/{pic_name}.jpg", 'png')
        except Exception as e:
            printer('error', e)
            pass
        finally:
            driver.quit()
        return get_selenium.selenium_object

    @staticmethod
    def selenium_content(url, isMobile=False, mobileModel=None, log=False, chromedriverPath=r''):
        """
        selenium 获取内容
        :param url: 访问的url
        :param isMobile: 是否手机模式访问
        :param mobileModel: 手机型号
        :param log: 显示日志
        :param chromedriverPath:  chromedriver路径
        :return:
        """
        if not chromedriverPath:
            print('Please download chromedriver: https://registry.npmmirror.com/binary.html?path=chromedriver/')
            exit()

        printer = lambda *args, **kwargs: print(*args, **kwargs) if log else False

        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 隐藏正受到自动测试软件的控制

        if isMobile:
            if isinstance(mobileModel, int):
                mobile_emulation = {"deviceName": get_selenium.mobileType[mobileModel - 1]}
            elif isinstance(mobileModel, dict):
                mobile_emulation = mobileModel
            else:
                mobile_emulation = {
                    "deviceMetrics": {"width": 192, "height": 108, "pixelRatio": 3.0},  # 定义设备高宽，像素比
                    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"  # 通过UA来模拟
                }
            chrome_options.add_experimental_option('mobileEmulation', mobile_emulation)

        driver = webdriver.Chrome(options=chrome_options, service=Service(chromedriverPath))  # python新版本
        # driver = webdriver.Chrome(options=chrome_options, executable_path='../../self/20191014_selenium_getTitle/chromedriver_win32/chromedriver.exe')  # python旧版本
        driver.set_window_rect(0, 0, 192, 108)  # setting position
        # driver.maximize_window()  # browser maximum
        driver.implicitly_wait(10)
        try:
            driver.get(url)
            printer('selenium visiting URL ==>', url)

            # region fill selenium_object
            try:
                get_selenium.selenium_object['url'] = driver.current_url
            except Exception as e:
                printer('url -> error:', e)
            try:
                get_selenium.selenium_object['title'] = driver.title
            except Exception as e:
                printer('title -> error:', e)
            try:
                get_selenium.selenium_object['page_content'] = driver.page_source
            except Exception as e:
                printer('page_content -> error:', e)
            # endregion

        except Exception as e:
            print('error', e)
            pass
        finally:
            driver.quit()
        return get_selenium.selenium_object

    @staticmethod
    def show_mobile_model(mobileModel=None):
        if mobileModel is None:
            print('You can choose these mobile model:')
            for order, i in enumerate(get_selenium.mobileType, 1):
                print(order, '==> ', i)
        else:
            print(mobileModel, '==>', get_selenium.mobileType[mobileModel - 1])


class requests_plus():
    @staticmethod
    def get_(url, reqNum=1, encode=None, **kwargs):
        for _ in range(reqNum):
            try:
                req = requests.get(url=url, **kwargs)
                encoding = {'utf-8': 'utf-8', 'UTF-8': 'UTF-8', 'utf8': 'utf-8', 'gbk': 'gbk', 'gb2312': 'gb18030', 'ISO-8859-1': 'utf-8'}
                req.encoding = encode or encoding.get(req.apparent_encoding, 'gbk')
                if req.status_code == 200:
                    return req
            except Exception as e:
                pass
        return False

    @staticmethod
    def get_picture(url, reqNum=1, savePath=r'.', saveName=r'', isDownload=True, log=False, **kwargs):
        printer = lambda *args, **kwargs: print(*args, **kwargs) if log else False
        saveName = saveName or time.strftime("%Y%m%d-%H%M%S.png")
        if isDownload and os.path.exists(fr'{savePath}/{saveName}'):
            print(fr'{savePath}/{saveName} 存在')
            return False
        browserhead = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}
        for _ in range(reqNum):
            try:
                req = requests.get(url=url, headers=kwargs.get('headers', browserhead), **kwargs)
                if req.status_code == 200:
                    if isDownload:
                        open(fr'{savePath}/{saveName}', 'wb').write(req.content)
                    return req
            except Exception as e:
                printer(e)
        return False


if __name__ == '__main__':
    # r = get_selenium.selenium_screenshot2pic(url='http://www.baidu.com', pic_name='www.baidu.com', isMobile=True)  # http://lqfbwvhz.vftg.vip/index.php http://rljwt.kityc.xyz/#/no_password
    # r = get_selenium.selenium_content('http://www.baidu.com')
    # print(r)
    # get_selenium.show_mobile_model()
    r = requests_plus.get_('http://www.baidu.com', 1, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'})
    print(r)
    pass
