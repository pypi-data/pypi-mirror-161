import os
import sys
import time
import pyperclip
import random
import chromedriver_autoinstaller as AutoChrome
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import *
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from python_anticaptcha import AnticaptchaClient, ImageToTextTask, AnticaptchaException


def get_status(driver: WebDriver):
    """
    If the driver can get the title of the page, it's alive, otherwise it's dead
    
    :param driver: The webdriver object
    :type driver: WebDriver
    :return: The status of the driver.
    """
    try:
        driver.title
    except:
        return "Dead"
    else:
        return "Alive"


def load_driver(chrome_options=None, mode=None, userId=None, port=9222, **kwargs) -> WebDriver:
    """
    It opens a Chrome browser with the specified options
    
    :param chrome_options: This is an instance of the ChromeOptions class. You can pass an existing
    instance of ChromeOptions to this parameter, or you can create a new instance of ChromeOptions
    :param mode: This is the mode you want to use. You can use multiple modes at once
    :param userId: This is the user ID that you want to use. This is used to create a cache folder for
    the user
    :param port: The port number that the Chrome browser will be running on, defaults to 9222 (optional)
    :return: A WebDriver object.
    """

    # userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    # userAgentMo = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
    # userAgent = UserAgent().random

    valid_mode_lst = [
        'fast',
        'cache',
        'debug',
        'secret'
    ]

    chrome_ver = AutoChrome.get_chrome_version().split('.')[0]
    chrome_driver_path = 'C:\\chromedriver\\'

    if not os.path.isdir('c:\\chromedriver'):
        os.mkdir('c:\\chromedriver')
    
    if chrome_options is None:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--window-position=850,0')
    
    chrome_options.add_argument('--disable-features=ChromeWhatsNewUI')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "test-type"])
    
    if not mode:

        pass

    else:

        if isinstance(mode, str):

            md = mode
            
            if md == 'fast':

                chrome_options.add_argument('disable-infobars')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-gpu')
                prefs = {'profile.default_content_setting_values': {'cookies' : 2, 'images': 2, 'plugins' : 2, 'popups': 2, 'geolocation': 2, 'notifications' : 2, 'auto_select_certificate': 2, 'fullscreen' : 2, 'mouselock' : 2, 'mixed_script': 2, 'media_stream' : 2, 'media_stream_mic' : 2, 'media_stream_camera': 2, 'protocol_handlers' : 2, 'ppapi_broker' : 2, 'automatic_downloads': 2, 'midi_sysex' : 2, 'push_messaging' : 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop' : 2, 'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement' : 2, 'durable_storage' : 2}}
                chrome_options.add_experimental_option('prefs', prefs)
                
            if md == 'cache':
                
                userDataFolder = 'c:/cache/{}'.format(userId)
                chrome_options.add_argument('--user-data-dir=' + userDataFolder)
                chrome_options.add_argument('--disk-cache-dir=' + userDataFolder)
            
            if md == 'debug':
                import subprocess
                try:
                    subprocess.Popen(rf'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port={port} --user-data-dir="C:\chrometemp"')
                except:
                    subprocess.Popen(rf'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe --remote-debugging-port={port} --user-data-dir="C:\chrometemp"')

                chrome_options = Options()                                                                    # 옵션객체 생성
                chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            
            if md == 'secret':
                chrome_options.add_argument('--incognito')
            
            if md not in valid_mode_lst:
                modes_text = ", ".join(valid_mode_lst)
                raise ValueError(f"Invalid Value : {mode}\nPlease Use below instead of {mode}\n\n{modes_text}\n\nUsage : load_driver(mode=['{random.choice(valid_mode_lst)}'])")
        else:
            for md in mode:
        
                if md == 'fast':

                    chrome_options.add_argument('disable-infobars')
                    chrome_options.add_argument('--disable-extensions')
                    chrome_options.add_argument('--disable-gpu')
                    prefs = {'profile.default_content_setting_values': {'cookies' : 2, 'images': 2, 'plugins' : 2, 'popups': 2, 'geolocation': 2, 'notifications' : 2, 'auto_select_certificate': 2, 'fullscreen' : 2, 'mouselock' : 2, 'mixed_script': 2, 'media_stream' : 2, 'media_stream_mic' : 2, 'media_stream_camera': 2, 'protocol_handlers' : 2, 'ppapi_broker' : 2, 'automatic_downloads': 2, 'midi_sysex' : 2, 'push_messaging' : 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop' : 2, 'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement' : 2, 'durable_storage' : 2}}
                    chrome_options.add_experimental_option('prefs', prefs)
                    
                if md == 'cache':
                    
                    userDataFolder = 'c:/cache/{}'.format(userId)
                    chrome_options.add_argument('--user-data-dir=' + userDataFolder)
                    chrome_options.add_argument('--disk-cache-dir=' + userDataFolder)
                
                if md == 'debug':
                    import subprocess
                    try:
                        subprocess.Popen(rf'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port={port} --user-data-dir="C:\chrometemp"')
                    except:
                        subprocess.Popen(rf'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe --remote-debugging-port={port} --user-data-dir="C:\chrometemp"')

                    chrome_options = Options()                                                                    # 옵션객체 생성
                    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
                
                if md == 'secret':
                    chrome_options.add_argument('--incognito')
                
                if md not in valid_mode_lst:
                    modes_text = ", ".join(valid_mode_lst)
                    raise ValueError(f"Invalid Value : {mode}\nPlease Use below instead of {mode}\n\n{modes_text}\n\nUsage : load_driver(mode=['{random.choice(valid_mode_lst)}'])")
    
    if os.path.isfile(f'c:\\chromedriver\\{chrome_ver}\\chromedriver.exe'):
        driver = webdriver.Chrome(executable_path=f'c:\\chromedriver\\{chrome_ver}\\chromedriver.exe', options=chrome_options, **kwargs)
    else:
        driver = webdriver.Chrome(executable_path=AutoChrome.install(path=chrome_driver_path), options=chrome_options, **kwargs)

    while len(driver.window_handles) > 1:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    return driver


def load_driver2(port=9222):
    import subprocess
    
    chrome_ver = AutoChrome.get_chrome_version().split('.')[0]
    chrome_driver_path = 'C:\\chromedriver\\'

    if not os.path.isdir('c:\\chromedriver'):
        os.mkdir('c:\\chromedriver')

    # userAgent = UserAgent().random
    try:
        subprocess.Popen(rf'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port={port} --user-data-dir="C:\chrometemp"')
    except:
        subprocess.Popen(rf'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe --remote-debugging-port={port} --user-data-dir="C:\chrometemp"')

    # d = DesiredCapabilities.CHROME
    # d['goog:loggingPrefs'] = { 'browser':'ALL' }
    chrome_options = Options()                                                                    # 옵션객체 생성
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    # chrome_options.add_argument(f"user-agent={userAgent}")
    try:
        driver = webdriver.Chrome(executable_path=f'c:\\chromedriver\\{chrome_ver}\\chromedriver.exe', options=chrome_options)
    except:
        AutoChrome.install(path=chrome_driver_path)
        driver = webdriver.Chrome(executable_path=f'c:\\chromedriver\\{chrome_ver}\\chromedriver.exe', options=chrome_options)
    
    if len(driver.window_handles) > 1:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    return driver


def load_cache_driver(userId, chrome_options = None, **kwargs):
    import warnings
    warnings.warn("load_cache_driver is deprecated. Use load_driver instead.", DeprecationWarning)
    return load_driver(chrome_options=chrome_options, mode=['cache'], userId=userId, **kwargs)


def n_login(driver: WebDriver, nid, pwd):

    driver.get('https://m.naver.com/aside/')
    
    time.sleep(.5)
    
    try:
        if driver.find_element(By.CSS_SELECTOR, '.MM_LOGINOUT').text == '로그아웃':
            return True
    except:
        pass

    driver.find_elements(By.CSS_SELECTOR, 'a[class="ss_a"]')[0].click()

    pyperclip.copy(nid)
    driver.find_elements(By.CSS_SELECTOR, '#id')[0].send_keys(Keys.CONTROL, 'v')
    time.sleep(0.5)

    pyperclip.copy(pwd)
    driver.find_elements(By.CSS_SELECTOR, '#pw')[0].send_keys(Keys.CONTROL, 'v')
    time.sleep(0.5)

    driver.find_elements(By.CSS_SELECTOR, 'button[class="btn_check"]')[0].click()
    time.sleep(1)

    now_url = driver.current_url
    source = driver.page_source

    flag = None

    if 'https://m.naver.com/aside/' == now_url:
        flag = True
    
    elif 'idRelease' in now_url and '대량생성' in source:
        flag = '로그인제한(대량생성ID)'

    elif 'sleepId' in now_url and '회원님의 아이디는 휴면 상태로 전환되었습니다.' in source:
        flag = '휴면'
    
    elif 'https://nid.naver.com/nidlogin.login' == now_url and '가입하지 않은 아이디이거나, 잘못된 비밀번호입니다.' in source:
        flag = False
    
    elif 'https://nid.naver.com/nidlogin.login' == now_url and '스팸성 홍보활동' in source:
        flag = '보호조치(스팸성 홍보활동)'
    
    elif 'idSafetyRelease' in now_url and '회원님의 아이디를 보호하고 있습니다.' in source and '개인정보보호 및 도용' in source:
        flag = '보호조치(개인정보보호및도용)'
    
    elif 'idSafetyRelease' in now_url and '회원님의 아이디를 보호하고 있습니다.' in source and '타인으로 의심' in source:
        flag = '보호조치(타인의심)'
    
    elif 'idSafetyRelease' in now_url and '회원님의 아이디를 보호하고 있습니다.' in source:
        flag = '보호조치'

    elif 'https://nid.naver.com/user2/help/contactInfo?m=viewPhoneInfo' == now_url and '회원정보에 사용할 휴대 전화번호를 확인해 주세요.' in source:
        flag = True

    elif 'deviceConfirm' in now_url and '새로운 기기(브라우저) 로그인' in source:
        flag = True

    else:
        flag = False
    
    if flag is not True and flag is not False:
        import requests
        requests.get(f'http://aaa.e-e.kr/problemid/insert.php?id={nid}&desc={flag}')
    
    return flag


def daum_mail_login(driver, did, pwd):

    try:
        driver.get('https://logins.daum.net/accounts/signinform.do?url=https%3A%2F%2Fmail.daum.net%2F')
    except:
        driver.refresh()
    driver.implicitly_wait(5)
    time.sleep(1)

    pyperclip.copy(did)
    driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(Keys.CONTROL + 'v')
    pyperclip.copy(pwd)
    driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(Keys.CONTROL + 'v')
    time.sleep(.5)
    driver.find_element(By.CSS_SELECTOR, 'label[class="lab_check"]').click()
    time.sleep(.5)
    driver.find_element(By.CSS_SELECTOR, 'button[id="loginBtn"]').click()
    driver.implicitly_wait(5)
    time.sleep(1)

    now_url = driver.current_url

    # 카카오 통합계정이면 
    if now_url == 'https://logins.daum.net/accounts/login.do?slevel=1':

        # 로그인 창
        driver.get('https://accounts.kakao.com/login?continue=https%3A%2F%2Flogins.daum.net%2Faccounts%2Fksso.do%3Frescue%3Dtrue%26url%3Dhttps%253A%252F%252Fmail.daum.net%252F')
        driver.implicitly_wait(3)
        time.sleep(1)

        # 아이디 비밀번호 입력
        pyperclip.copy(did)
        driver.find_element(By.CSS_SELECTOR, 'input[validator="email_or_phone_or_kakaoid"]').send_keys(Keys.CONTROL + 'v')
        pyperclip.copy(pwd)
        driver.find_element(By.CSS_SELECTOR, 'input[validator="password"]').send_keys(Keys.CONTROL + 'v')
        time.sleep(.5)
        driver.execute_script(""" document.querySelector('input[name="stay_signed_in"]').click() """)
        time.sleep(.5)
        driver.find_element(By.CSS_SELECTOR, 'button[class="btn_g btn_confirm submit"]').click()
        driver.implicitly_wait(5)

        # 메일쓰기 버튼 나올때까지 대기
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'button[class="btn_comm btn_write"]')))
        time.sleep(1)

    else:

        try:
            WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'button[class="btn_comm btn_write"]')))
            time.sleep(1)
        except:
            driver.find_element(By.CSS_SELECTOR, 'a[id="afterBtn"]').click()
            driver.implicitly_wait(10)
            time.sleep(2)


def t_login(driver, tid, pwd):
    try:
        driver.find_element(By.CSS_SELECTOR, 'a[href="/login"]').click()
        driver.implicitly_wait(5)
        time.sleep(.5)

        pyperclip.copy(tid)
        driver.find_element(By.CSS_SELECTOR, 'input[type="text"]').send_keys(Keys.CONTROL, 'v')
        time.sleep(.5)
        pyperclip.copy(pwd)
        driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(Keys.CONTROL, 'v')
        time.sleep(.5)

        driver.find_element(By.CSS_SELECTOR, 'div[role="button"]').click()
        driver.implicitly_wait(5)
        time.sleep(.5)
    except:
        print('로그인이 되어 있습니다.')
    driver.get('https://twitter.com')
    time.sleep(1)
    if driver.current_url == 'https://twitter.com/home':
        return True
    else:
        return False


def line_login(driver: WebDriver, line_email: str, line_passwd: str):
    login_flag = False
    driver.implicitly_wait(3)
    driver.get('https://m.naver.com/aside/')
    if driver.find_element(By.CSS_SELECTOR, 'a.MM_LOGINOUT').text == '로그아웃':
        login_flag = True
        return login_flag

    try:
        driver.get('https://access.line.me/oauth2/v2.1/noauto-login?loginState=RqKRHGGcrATtnP3SI7gc3I&loginChannelId=1426360231&returnUri=%2Foauth2%2Fv2.1%2Fauthorize%2Fconsent%3Fscope%3Dprofile%2Bfriends%2Bmessage.write%2Btimeline.post%2Bphone%2Bemail%2Bopenid%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fnid.naver.com%252Foauth%252Fglobal%252FlineCallback%26state%3D0120522838%26client_id%3D1426360231#/')
    except WebDriverException:
        login_flag = False
        return login_flag
    
    try:
        email_input_el = WebDriverWait(driver, 3).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'input[name="tid"]')))	
    except:
        if driver.find_elements(By.CSS_SELECTOR, 'button.c-button.l-btn.c-button--allow'):
            driver.find_elements(By.CSS_SELECTOR, 'button.c-button.l-btn.c-button--allow')[0].click()
        else:
            print('이메일 입력창을 찾을 수 없습니다. 담당자에게 문의해주세요.')
            sys.exit()
    else:
        try:
            password_input_el = WebDriverWait(driver, 3).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'input[name="tpasswd"]')))	
        except:
            print('패스워드 입력창을 찾을 수 없습니다. 담당자에게 문의해주세요.')
            sys.exit()
        else:
            email_input_el.send_keys(line_email)
            time.sleep(1)
            password_input_el.send_keys(line_passwd)
            time.sleep(1)
            driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
            time.sleep(1)

    # 알림창 한 번 처리하고 실패시 return False, 로그인 성공 후 현재 도메인 네이버일 경우 return True
    try:
        alert  = driver.switch_to.alert
        alert.accept()
        
        driver.quit()
        
        driver.get('https://www.naver.com')
        time.sleep(5)
        
        driver.get('https://access.line.me/oauth2/v2.1/noauto-login?loginState=RqKRHGGcrATtnP3SI7gc3I&loginChannelId=1426360231&returnUri=%2Foauth2%2Fv2.1%2Fauthorize%2Fconsent%3Fscope%3Dprofile%2Bfriends%2Bmessage.write%2Btimeline.post%2Bphone%2Bemail%2Bopenid%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fnid.naver.com%252Foauth%252Fglobal%252FlineCallback%26state%3D0120522838%26client_id%3D1426360231#/')
        time.sleep(5)
        
        try:
            email_input_el = WebDriverWait(driver, 3).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'input[name="tid"]')))	
        except:
            if driver.find_elements(By.CSS_SELECTOR, 'button.c-button.l-btn.c-button--allow'):
                driver.find_elements(By.CSS_SELECTOR, 'button.c-button.l-btn.c-button--allow')[0].click()
            else:
                print('이메일 입력창을 찾을 수 없습니다. 담당자에게 문의해주세요.')
                sys.exit()
        else:
            try:
                password_input_el = WebDriverWait(driver, 3).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'input[name="tpasswd"]')))	
            except:
                print('패스워드 입력창을 찾을 수 없습니다. 담당자에게 문의해주세요.')
                sys.exit()
            else:
                email_input_el.send_keys(line_email)
                time.sleep(1)
                password_input_el.send_keys(line_passwd)
                time.sleep(1)
                driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
                time.sleep(1)
        
        try:
            if driver.current_url in "https://www.naver.com/":
                login_flag = True
                return login_flag
            else:
                
                if driver.find_elements(By.CSS_SELECTOR, 'button.c-button.l-btn.c-button--allow'):
                    driver.find_elements(By.CSS_SELECTOR, 'button.c-button.l-btn.c-button--allow')[0].click()

                    time.sleep(1)

                    if driver.current_url in "https://www.naver.com/":
                        login_flag = True
                        return login_flag
                
                if driver.find_elements(By.CSS_SELECTOR, 'input#btnSubmit.btn_global[type="submit"][title="Sign Up"]'):
                    
                    while driver.find_elements(By.CSS_SELECTOR, 'input#btnSubmit.btn_global[type="submit"][title="Sign Up"]'):
                        driver.find_elements(By.CSS_SELECTOR, 'input#btnSubmit.btn_global[type="submit"][title="Sign Up"]')[0].click()
                        try:
                            WebDriverWait(driver, 2).until(expected_conditions.alert_is_present(), "")
                            alert = driver.switch_to.alert
                        except:
                            time.sleep(2)
                        else:
                            alert_msg = alert.text
                            alert.accept()

                            if 'Temporarily unavailable. Please try again later' in alert_msg:
                                login_flag = False
                                return login_flag


                    time.sleep(1)

                    if driver.find_elements(By.CSS_SELECTOR, 'a[href="javascript:goStart();"]'):
                        driver.find_elements(By.CSS_SELECTOR, 'a[href="javascript:goStart();"]')[0].click()
                    
                    time.sleep(1)

                    if driver.current_url in "https://www.naver.com/":
                        login_flag = True
                        return login_flag
                
                try:
                    driver.find_element(By.CSS_SELECTOR, 'p.mdFormErrorTxt01')
                    if "잘못 입력된 항목이 있습니다." in driver.find_element(By.CSS_SELECTOR, 'p.mdFormErrorTxt01').text:
                        login_flag = '입력오류'
                        return login_flag
                except NoSuchElementException:
                    pass
            
                try:
                    driver.find_element(By.CSS_SELECTOR, 'div.top_title > br')
                    if "보호(잠금)" in driver.find_element(By.CSS_SELECTOR, 'div.top_title').text.split('\n')[1]:
                        login_flag = '보호'
                        return login_flag
                except NoSuchElementException:
                    pass
                
                try:
                    driver.find_element(By.CSS_SELECTOR, 'div.warning > div.warning_box')
                    if "영구 이용정지" in driver.find_element(By.CSS_SELECTOR, 'div.warning > div.warning_box').text:
                        login_flag = '영구 이용정지'
                        return login_flag
                except NoSuchElementException:
                    pass

                return login_flag
        except UnexpectedAlertPresentException:
            try:
                driver.switch_to.alert.accept()
            except:
                pass
            login_flag = False
            return login_flag

    # 알림창 없을 경우 위 try 구문 에러, 현재 주소 기준 return 값으로 login_log 기록     
    except:
        try:            
            if driver.current_url in "https://www.naver.com/":
                login_flag = True
                return login_flag
            
            else:

                if driver.find_elements(By.CSS_SELECTOR, 'button.c-button.l-btn.c-button--allow'):
                    driver.find_elements(By.CSS_SELECTOR, 'button.c-button.l-btn.c-button--allow')[0].click()

                    time.sleep(1)

                    if driver.current_url in "https://www.naver.com/":
                        login_flag = True
                        return login_flag
                
                if driver.find_elements(By.CSS_SELECTOR, 'input#btnSubmit.btn_global[type="submit"][title="Sign Up"]'):
                    
                    while driver.find_elements(By.CSS_SELECTOR, 'input#btnSubmit.btn_global[type="submit"][title="Sign Up"]'):
                        driver.find_elements(By.CSS_SELECTOR, 'input#btnSubmit.btn_global[type="submit"][title="Sign Up"]')[0].click()
                        try:
                            WebDriverWait(driver, 2).until(expected_conditions.alert_is_present(), "")
                            alert = driver.switch_to.alert
                        except:
                            time.sleep(2)
                        else:
                            alert_msg = alert.text
                            alert.accept()

                            if 'Temporarily unavailable. Please try again later' in alert_msg:
                                login_flag = False
                                return login_flag


                    time.sleep(1)

                    if driver.find_elements(By.CSS_SELECTOR, 'a[href="javascript:goStart();"]'):
                        driver.find_elements(By.CSS_SELECTOR, 'a[href="javascript:goStart();"]')[0].click()
                    
                    time.sleep(1)

                    if driver.current_url in "https://www.naver.com/":
                        login_flag = True
                        return login_flag

                try:
                    driver.find_element(By.CSS_SELECTOR, 'p.mdFormErrorTxt01')
                    if "잘못 입력된 항목이 있습니다." in driver.find_element(By.CSS_SELECTOR, 'p.mdFormErrorTxt01').text:
                        login_flag = '입력오류'
                        return login_flag
                except NoSuchElementException:
                    pass
            
                try:
                    driver.find_element(By.CSS_SELECTOR, 'div.top_title > br')
                    if "보호(잠금)" in driver.find_element(By.CSS_SELECTOR, 'div.top_title').text.split('\n')[1]:
                        login_flag = '보호'
                        return login_flag
                except NoSuchElementException:
                    pass

                try:
                    driver.find_element(By.CSS_SELECTOR, 'div.warning > div.warning_box')
                    if "영구 이용정지" in driver.find_element(By.CSS_SELECTOR, 'div.warning > div.warning_box').text:
                        login_flag = '영구 이용정지'
                        return login_flag
                except NoSuchElementException:
                    pass
                
                return login_flag
        
        except Exception:
            try:
                driver.switch_to.alert.accept()
            except:
                pass
            login_flag = False
            return login_flag


def scrollDownUntilPageEnd(driver, SCROLL_PAUSE_SEC = 1):
    """
    It scrolls down the page until the page height is the same as the last scroll height
    
    :param driver: the webdriver object
    :param SCROLL_PAUSE_SEC: The number of seconds to wait between each scroll, defaults to 1 (optional)
    :return: The return value is the height of the document in pixels.
    """
    
    # 스크롤 높이 가져옴
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
    except:
        return False
    while True:
        # 끝까지 스크롤 다운
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 1초 대기
        time.sleep(SCROLL_PAUSE_SEC)

        # 스크롤 다운 후 스크롤 높이 다시 가져옴
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # 끝까지 스크롤 다운
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # 1초 대기
            time.sleep(SCROLL_PAUSE_SEC)

            # 스크롤 다운 후 스크롤 높이 다시 가져옴
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            break
        last_height = new_height
    return True


def solve_reCAPTCHA(driver: WebDriver):
    """
    It takes a webdriver as an argument, finds the reCAPTCHA key and the current URL, and then uses the
    anticaptcha API to solve the reCAPTCHA
    
    :param driver: WebDriver
    :type driver: WebDriver
    :return: The return value is the result of the last expression in the function body, if any. If the
    function doesn't have a return statement, the function returns None.
    """
    
    from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless

    try:
        target_site_url = driver.current_url
        target_site_key = driver.execute_script('''return document.querySelector('[data-sitekey]').getAttribute('data-sitekey');''')
    except:
        print('해당 사이트의 reCAPTCHA Key를 찾을 수 없습니다.')
        return False

    API_KEY = 'b336be7de932b65c877403893a382713'

    solver = recaptchaV2Proxyless()
    solver.set_verbose(1)
    solver.set_key(API_KEY)
    solver.set_website_url(target_site_url)
    solver.set_website_key(target_site_key)
    #set optional custom parameter which Google made for their search page Recaptcha v2
    #solver.set_data_s('"data-s" token from Google Search results "protection"')

    g_response = solver.solve_and_return_solution()
    if g_response != 0:
        # print("g-response: "+g_response)
        pass
    else:
        print("task finished with error "+solver.error_code)
    
    result_flag = driver.execute_script(f'''document.getElementById("g-recaptcha-response").innerHTML = "{g_response}"''')

    return result_flag == None
