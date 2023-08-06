from typing import List, Union
from clicknium.core.models.uielement import UiElement
from clicknium.locator import _Locator
from clicknium.core.service.invokerservice import _ExceptionHandle, _InvokerService
from clicknium.core.models.web.webelement import WebElement


class BrowserTab(object):    

    def __init__(self, tab_object):
        self._tab = tab_object 

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, trace):
        self.close()

    @property
    @_ExceptionHandle.try_except
    def title(self) -> str:
        """
            Get tab's title.
                                
            Returns:
                str
        """
        return self._tab.PageTitle

    @property
    @_ExceptionHandle.try_except
    def url(self) -> str:
        """
            Get tab's url.
                                
            Returns:
                str
        """
        return self._tab.Url

    @property
    @_ExceptionHandle.try_except
    def is_active(self) -> bool:
        """
            Determine if the current tab is active.
                                
            Returns:
                bool
        """
        return self._tab.IsActive

    @property
    @_ExceptionHandle.try_except
    def browser(self):
        """
            Get the browser of the current tab.
                                
            Returns:
                Browser
        """
        from clicknium.core.models.web.browser import Browser
        return Browser(self._tab.Browser)

    @_ExceptionHandle.try_except
    def close(self) -> None:
        """
            Close the current tab.

            Returns:
                None
        """
        self._tab.Close()

    @_ExceptionHandle.try_except
    def refresh(self) -> None:
        """
            Refresh the current tab.

            Returns:
                None
        """
        self._tab.Refresh()

    @_ExceptionHandle.try_except
    def goto(
        self,
        url: str
    ) -> None:
        """
            Go to other website in current tab.
 
            Parameters:

                url[Required]: website string, ex: https://www.bing.com
                                            
            Returns:
                None
        """
        self._tab.Navigate(url)

    @_ExceptionHandle.try_except
    def activate(
        self,
        is_topmost: bool = True
    ) -> None:
        """
            Activate current tab.
 
            Parameters:

                is_topmost: bool, whether to set the windows top most
                                            
            Returns:
                None
        """
        self._tab.Activate(is_topmost)

    def find_element(
        self,
        locator: Union[_Locator, str],
        locator_variables: dict = {}
    ) -> WebElement:
        """
            In current opened browser, initialize ui element by the given locator.

            Remarks: 
                1.Use "ctrl + f10" to record locator.
                2.It should be used like clicknium.chrome.open("https://bing.com").find_element(), it is different with clicknium.find_element() when locating the ui element.
                    clicknium.find_element() is for both web and window's uielement, and does not specified a scope to locate the element
                    clicknium.chrome.open("https://bing.com").find_element() will locate element in the specified browser tab
 
            Parameters:
                locator[Required]: the visit path of locator for target UI element, eg: 'locator.chrome.bing.search_sb_form_q', locator store is chrome, and locator name is search_sb_form_q  

                locator_variables: set to initialize parameters in locator, eg: { "row": 1,  "column": 1}, more about variable, please refer to https://www.clicknium.com/documents/concepts/parametric_locator  
 
            Returns:
                WebElement object
        """
        ele = _InvokerService.find_element_web(self._tab, locator, locator_variables)
        return WebElement(ele)

    def find_elements(
        self,
        locator: Union[_Locator, str],
        locator_variables: dict = {},
        timeout: int = 30
    ) -> List[WebElement]:

        """
            Find elements by the given locator.

            Remarks: 

                1.Use "ctrl + f10" to record locator.
 
            Parameters:
                locator[Required]: the visit path of locator for target UI element, eg: 'locator.chrome.bing.search_sb_form_q', locator store is chrome, and locator name is search_sb_form_q  

                locator_variables: set to initialize parameters in locator, eg: { "row": 1,  "column": 1}, more about variable, please refer to https://www.clicknium.com/documents/concepts/parametric_locator  

                timeout: timeout for the operation, unit is second, default value is 30 seconds
 
            Returns:
                list of WebElement object
        """
        elements = []
        results = _InvokerService.find_elements_web(self._tab, locator, locator_variables, timeout)
        if results:
            for element in results:
                elements.append(WebElement(element))
        return elements

    def wait_disappear(
        self,
        locator: Union[_Locator, str],
        locator_variables: dict = {},
        wait_timeout: int = 30
    ) -> bool:
        """
            In current opened browser, wait for the element disappear.
 
            Parameters:
                locator[Required]: the visit path of locator for target UI element, eg: 'locator.chrome.bing.search_sb_form_q', locator store is chrome, and locator name is search_sb_form_q  

                locator_variables: set to initialize parameters in locator, eg: { "row": 1,  "column": 1}, more about variable, please refer to https://www.clicknium.com/documents/concepts/parametric_locator  

                wait_timeout: wait timeout for the operation, unit is second, default value is 30 seconds
 
            Returns:
                bool, return True if the element is disappear in given time or return False
        """ 
        result = _InvokerService.wait_disappear_web(self._tab, locator, locator_variables, wait_timeout)
        return True if result else False

    def wait_appear(
        self,
        locator: Union[_Locator, str],
        locator_variables: dict = {},
        wait_timeout: int = 30
    ) -> WebElement:
        """
            In current opened browser, wait for the element appear.
 
            Parameters:
                locator[Required]: the visit path of locator for target UI element, eg: 'locator.chrome.bing.search_sb_form_q', locator store is chrome, and locator name is search_sb_form_q  

                locator_variables: set to initialize parameters in locator, eg: { "row": 1,  "column": 1}, more about variable, please refer to https://www.clicknium.com/documents/concepts/parametric_locator  

                wait_timeout: wait timeout for the operation, unit is second, default value is 30 seconds
 
            Returns:
                WebElement object, or None if the element is not appear
        """ 
        ele = _InvokerService.wait_appear_web(self._tab, locator, locator_variables, wait_timeout)
        if ele:
            return WebElement(ele)
        return None

    def is_existing(
        self,
        locator: Union[_Locator, str],
        locator_variables: dict = {},
        timeout: int = 30
    ) -> bool: 
        """
            In current opened browser, check whether the ui element exist or not.
 
            Parameters:
                locator[Required]: the visit path of locator for target UI element, eg: 'locator.chrome.bing.search_sb_form_q', locator store is chrome, and locator name is search_sb_form_q  

                locator_variables: set to initialize parameters in locator, eg: { "row": 1,  "column": 1}, more about variable, please refer to https://www.clicknium.com/documents/concepts/parametric_locator  

                timeout: timeout for the operation, unit is second, default value is 30 seconds
 
            Returns:
                return True if ui element exist, or return False
        """    
        result = _InvokerService.is_existing_web(self._tab, locator, locator_variables, timeout)
        return True if result else False    

    