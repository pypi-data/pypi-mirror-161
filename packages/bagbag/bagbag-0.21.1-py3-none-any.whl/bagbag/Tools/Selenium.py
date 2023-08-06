from __future__ import annotations

from selenium import webdriver
from typing import List
from selenium.webdriver.common.by import By
import selenium
from selenium.webdriver.common.keys import Keys

import time

# > The SeleniumElement class is a wrapper for the selenium.webdriver.remote.webelement.WebElement
# class
class SeleniumElement():
    def __init__(self, element:selenium.webdriver.remote.webelement.WebElement):
        self.element = element
    
    def Clear(self) -> SeleniumElement:
        """
        Clear() clears the text if it's a text entry element
        """
        self.element.clear()
        return self
    
    def Click(self) -> SeleniumElement:
        """
        Click() is a function that clicks on an element
        """
        self.element.click()
        return self
    
    def Text(self) -> str:
        """
        The function Text() returns the text of the element
        :return: The text of the element.
        """
        return self.element.text

    def Attribute(self, name:str) -> str:
        """
        This function returns the value of the attribute of the element
        
        :param name: The name of the element
        :type name: str
        :return: The attribute of the element.
        """
        return self.element.get_attribute(name)
    
    def Input(self, string:str) -> SeleniumElement:
        """
        The function Input() takes in a string and sends it to the element
        
        :param string: The string you want to input into the text box
        :type string: str
        """
        self.element.send_keys(string)
        return self
    
    def Submit(self) -> SeleniumElement:
        """
        Submit() is a function that submits the form that the element belongs to
        """
        self.element.submit()
        return self
    
    def PressEnter(self) -> SeleniumElement:
        """
        It takes the element that you want to press enter on and sends the enter key to it
        """
        self.element.send_keys(Keys.ENTER)
        return self

class Selenium():
    def __init__(self, seleniumServer:str=None, disableLoadImage=False, sessionID=None):
        """
        If the seleniumServer is not None, then the driver is a Remote WebDriver, otherwise it's a
        Chrome WebDriver
        
        :param seleniumServer: The URL of the Selenium server. If you're running Selenium locally, this
        will be http://localhost:4444/wd/hub
        :type seleniumServer: str
        :param disableLoadImage: If set to True, the browser will not load images, defaults to False
        (optional)
        :param sessionID: If you already have a session ID, you can pass it in here
        """
        chrome_options = webdriver.ChromeOptions()

        if disableLoadImage:
            prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", prefs)

        if seleniumServer:
            if not seleniumServer.endswith("/wd/hub"):
                seleniumServer = seleniumServer + "/wd/hub"
            self.driver = webdriver.Remote(
                command_executor=seleniumServer,
                options=chrome_options
            )
        else:
            self.driver = webdriver.Chrome(
                options=chrome_options,
            )
        
        if sessionID:
            self.Close()
            self.driver.session_id = sessionID
    
    def Find(self, xpath:str, waiting=True) -> SeleniumElement|None:
        """
        It will keep trying to find the element until it finds it or keep waiting
        
        :param xpath: The xpath of the element you want to find
        :type xpath: str
        :param waiting: If True, the function will wait until the element is found. If False, it will
        raise an exception if the element is not found, defaults to True (optional)
        :return: SeleniumElement
        """
        while True:
            try:
                el = self.driver.find_element(By.XPATH, xpath)
                return SeleniumElement(el)
            except selenium.common.exceptions.NoSuchElementException as e: 
                if waiting:
                    time.sleep(1)
                else:
                    return None

        # import ipdb
        # ipdb.set_trace()
    
    def StatusCode(self) -> int:
        self.driver.stat
    
    def ResizeWindow(self, width:int, height:int):
        """
        :param width: The width of the window in pixels
        :type width: int
        :param height: The height of the window in pixels
        :type height: int
        """
        self.driver.set_window_size(width, height)
    
    def ScrollRight(self, pixel:int):
        """
        ScrollRight(self, pixel:int) scrolls the page to the right by the number of pixels specified in
        the pixel parameter
        
        :param pixel: The number of pixels to scroll by
        :type pixel: int
        """
        self.driver.execute_script("window.scrollBy("+str(pixel)+",0);")
    
    def ScrollLeft(self, pixel:int):
        """
        Scrolls the page left by the number of pixels specified in the parameter.
        
        :param pixel: The number of pixels to scroll by
        :type pixel: int
        """
        self.driver.execute_script("window.scrollBy("+str(pixel*-1)+",0);")

    def ScrollUp(self, pixel:int):
        """
        Scrolls up the page by the number of pixels specified in the parameter.
        
        :param pixel: The number of pixels to scroll up
        :type pixel: int
        """
        self.driver.execute_script("window.scrollBy(0, "+str(pixel*-1)+");")

    def ScrollDown(self, pixel:int):
        """
        Scrolls down the page by the specified number of pixels
        
        :param pixel: The number of pixels to scroll down
        :type pixel: int
        """
        self.driver.execute_script("window.scrollBy(0, "+str(pixel)+");")

    def Url(self) -> str:
        """
        > The `Url()` function returns the current URL of the page
        :return: The current url of the page
        """
        return self.driver.current_url
    
    def Cookie(self) -> List[dict]:
        """
        This function gets the cookies from the driver and returns them as a list of dictionaries
        """
        return self.driver.get_cookies()
    
    def SetCookie(self, cookie_dict:dict):
        """
        This function takes a dictionary of cookie key-value pairs and adds them to the current session
        
        :param cookie_dict: A dictionary object, with mandatory keys as follows:
        :type cookie_dict: dict
        """
        self.driver.add_cookie(cookie_dict)
    
    def Refresh(self):
        """
        Refresh() refreshes the current page
        """
        self.driver.refresh()
    
    def GetSession(self) -> str:
        """
        The function GetSession() returns the session ID of the current driver
        :return: The session ID of the driver.
        """
        return self.driver.session_id
    
    def Get(self, url:str):
        """
        The function Get() takes a string as an argument and uses the driver object to navigate to the
        url.
        
        :param url: The URL of the page you want to open
        :type url: str
        """
        self.driver.get(url)
    
    def PageSource(self) -> str:
        """
        It returns the page source of the current page
        :return: The page source of the current page.
        """
        return self.driver.page_source

    def Title(self) -> str:
        """
        The function Title() returns the title of the current page
        :return: The title of the page
        """
        return self.driver.title
    
    def Close(self):
        """
        The function closes the browser window and quits the driver
        """
        self.driver.close()
        self.driver.quit()

if __name__ == "__main__":
    # se = Selenium()
    se = Selenium("http://127.0.0.1:4444")
    se.Get("https://find-and-update.company-information.service.gov.uk/")
    inputBar = se.Find("/html/body/div[1]/main/div[3]/div/form/div/div/input")
    inputBar.Input("ade")
    button = se.Find("/html/body/div[1]/main/div[3]/div/form/div/div/button")
    button.Click()
    se.Close()

