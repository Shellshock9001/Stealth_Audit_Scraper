from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import time
import argparse
import os
import sys

def create_profile():
    profile = FirefoxProfile()
    if args.proxy is not None:
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.socks", args.proxy)
        profile.set_preference("network.proxy.socks_port", args.proxy_port)
        profile.set_preference("network.proxy.socks_remote_dns", True)
    profile.set_preference("browser.privatebrowsing.autostart", True)
    profile.update_preferences()
    return profile

def load_browser():
    profile = create_profile()
    options = Options()
    options.headless = args.headless
    driver = webdriver.Firefox(options=options, firefox_profile=profile)
    return driver

def load_website(driver):
    try:
        print(f'[+] Attempting to visit {args.url}')
        print('[+] Clearing all cookies...')
        driver.delete_all_cookies()
        driver.get(args.url)
        time.sleep(2)
        # Check if login page is displayed
        if is_login_page(driver):
            if args.username and args.password:
                login_to_stealthaudit(driver, args.username, args.password)
            else:
                sys.exit('[-] Login required but no username and password provided.')
        else:
            print('[+] No login required.')
        time.sleep(3)
        navigate_to_users(driver)
    except Exception as e:
        sys.exit(f'[-] Failed loading website: {e}')

def is_login_page(driver):
    try:
        # Adjust the selectors based on the actual login page elements
        driver.find_element(By.ID, 'UserName')  # Example ID for username field
        driver.find_element(By.ID, 'Password')  # Example ID for password field
        return True
    except:
        return False

def login_to_stealthaudit(driver, username, password):
    try:
        print('[+] Attempting to log in...')
        username_field = driver.find_element(By.ID, 'UserName')
        password_field = driver.find_element(By.ID, 'Password')
        login_button = driver.find_element(By.ID, 'btnLogin')

        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()
        time.sleep(3)
        print('[+] Login successful.')
    except Exception as e:
        sys.exit(f'[-] Login failed: {e}')

def navigate_to_users(driver):
    print('[+] Navigating through the menu...')
    try:
        # Update these XPaths based on your actual menu structure
        # Click Active Directory
        driver.find_element(By.XPATH, "//div[text()='Active Directory']").click()
        time.sleep(1)
        # Click Users
        driver.find_element(By.XPATH, "//div[text()='Users']").click()
        time.sleep(1)
        # Click User Tokens or the relevant section
        driver.find_element(By.XPATH, "//div[text()='User Token']").click()
        time.sleep(1)
        # Switch to the main content iframe if necessary
        driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[contains(@src, 'UserToken')]"))
        enumerate_users(driver)
    except Exception as e:
        sys.exit(f'[-] Failed navigating the menu: {e}')

def enumerate_users(driver):
    print('[+] Enumerating Users...')
    while True:
        try:
            # Adjust the XPath to match the user table in your application
            user_rows = driver.find_elements(By.XPATH, "//div[@class='dhx_grid_content']/table/tbody/tr")
            if not user_rows:
                print('[-] No user rows found on this page.')
                break
            for row in user_rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) >= 3:
                    nt_acc = cells[1].text.strip()
                    user = cells[2].text.strip()
                    print(f'NT_Account: {nt_acc}\tName: {user}')
                    write_accounts(user, nt_acc)
            if not go_to_next_page(driver):
                break
        except Exception as e:
            print(f'[-] Error during user enumeration: {e}')
            break

def go_to_next_page(driver):
    try:
        # Adjust the XPath to the 'Next' button in your pagination controls
        next_button = driver.find_element(By.XPATH, "//div[@class='dhxtoolbar_btn dhxtoolbar_btn_def'][@title='Next page']")
        if 'dhxtoolbar_btn_dis' not in next_button.get_attribute('class'):
            next_button.click()
            time.sleep(2)
            return True
        else:
            print('[+] Reached the last page.')
            return False
    except Exception as e:
        print(f'[-] Error while navigating to the next page: {e}')
        return False

def write_accounts(user, nt_acc):
    with open(args.outfile, 'a') as outfile:
        outfile.write(f'{nt_acc}:{user}\n')

def argparser():
    parser = argparse.ArgumentParser(description="StealthAUDIT Scraper >:D")
    parser.add_argument("-o", "--outfile", help="The file to write users to.", default=f'{os.getcwd()}/ad_users.txt')
    parser.add_argument("-u", "--url", help="The webserver URL (e.g., http://10.0.0.1:80).", required=True)
    parser.add_argument("-p", "--proxy", help="The proxy IP (e.g., 10.0.0.1).", default=None)
    parser.add_argument("-pp", "--proxy_port", type=int, help="The proxy port (e.g., 1080).", default=None)
    parser.add_argument("-U", "--username", help="Username for login.", default=None)
    parser.add_argument("-P", "--password", help="Password for login.", default=None)
    parser.add_argument("--headless", help="Run browser in headless mode.", action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    args = argparser()
    driver = load_browser()
    load_website(driver)
    driver.quit()
    sys.exit('[+] Done!')
