from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException

class BrowserNotInstalledException(Exception):
    """
    Raised when a web browser is not installed in the default Program Files directories
    """
    pass