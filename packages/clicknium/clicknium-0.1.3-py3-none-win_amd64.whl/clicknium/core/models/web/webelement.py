from clicknium.core.models.uielement import UiElement
from clicknium.core.service.invokerservice import _ExceptionHandle

class WebElement(UiElement):

    def __init__(self, element):
        super(WebElement, self).__init__(element)

    @property
    @_ExceptionHandle.try_except
    def parent(self):
        """
            Get parent element.
                                
            Returns:
                WebElement object if it was found, or None if not
        """
        if self._element.Parent:
            return WebElement(self._element.Parent)
        return None

    @property
    @_ExceptionHandle.try_except
    def children(self):
        """
            Get element's children elements.
                                
            Returns:
                list of WebElement object, a list with elements if any was found or an empty list if not
        """
        child_list = []
        if self._element.Children:            
            for child in self._element.Children:
                child_list.append(WebElement(child))
        return child_list

    @property
    @_ExceptionHandle.try_except
    def next_sibling(self):
        """
            Get next sibling element.
                                
            Returns:
                WebElement object if it was found, or None if not
        """
        if self._element.NextSibling:
            return WebElement(self._element.NextSibling)
        return None

    @property
    @_ExceptionHandle.try_except
    def previous_sibling(self):
        """
            Get previous sibling element.
                                
            Returns:
                WebElement object if it was found, or None if not
        """
        if self._element.PreviousSibling:
            return WebElement(self._element.PreviousSibling)
        return None
    
    @_ExceptionHandle.try_except
    def child(self, index: int):
        """
            Get child element with its index.

            Parameters:
                index[Required]: index specified, get the nth child
                                
            Returns:
                WebElement object if it was found, or None if not
        """
        child_element = self._element.Child(index)
        if child_element:
            return WebElement(self._element.Child(index))
        return None

    @_ExceptionHandle.try_except
    def set_property(
        self,
        name: str,
        value: str,
        timeout: int = 30
    ) -> None:
        """
            Set web element's property value.
 
            Parameters:

                name[Required]: property name, different ui elements may support different property list

                value[Required]: property value

                timeout: timeout for the operation, unit is second, default value is 30 seconds
                                            
            Returns:
                None
        """
        self._element.SetProperty(name, value, timeout * 1000)

    @_ExceptionHandle.try_except
    def execute_js(
        self,
        javascript_code: str, 
        method: str = '', 
        timeout: int = 30
    ) -> str:
        """
            Execute javascript code snippet for the target element.

            Remarks: 
                1.For javascript code, use "_context$.currentElement." as the target element. 

                2.For parameter "method", valid string should like "run()", or when passing parameters should like "run("execute js", 20)".
 
            Parameters:

                javascript_code[Required]:  javascript code snippet to be executed upon target element.

                method: the method to be invoked should be defined in the javascript file. If any parameter need to passed to the method, it can be included in this parameter value, for eg.: SetText("test").

                timeout: timeout for the operation, unit is second, default value is 30 seconds
                                            
            Returns:
                str
        """
        return self._element.ExecuteJavaScript(javascript_code, method, timeout * 1000)

    @_ExceptionHandle.try_except
    def execute_js_file(
        self,
        javascript_file: str, 
        method: str = '', 
        timeout: int = 30
    ) -> str:
        """
            Execute javascript file for the target element.

            Remarks: 
                1.For javascript script, use "_context$.currentElement." as the target element. 

                2.For method invoke, valid method string should like "run()", or when passing parameters should like "run("execute js", 20)".
 
            Parameters:

                javascript_file[Required]: javascript file path, eg.: "c:\\test\\test.js".

                method: the method to be invoked should be defined in the javascript file. If any parameter need to passed to the method, it can be included in this parameter value, for eg.: SetText("test").

                timeout: timeout for the operation, unit is second, default value is 30 seconds
                                            
            Returns:
                str
        """
        with open(javascript_file, "r") as f:
            javascript_code = f.read()
        return self._element.ExecuteJavaScript(javascript_code, method, timeout * 1000)
