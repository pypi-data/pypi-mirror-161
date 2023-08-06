# Thursday
Thursday reduces the time it takes to get up and running with [Selenium](https://www.selenium.dev/).
## Installation
Use [pip](https://pip.pypa.io/en/stable/) to install _thursday_ as follows:
```cmd
pip install thursday
```
## Usage (Examples)
### Instantiating ChromeDriver
```python
from thursday import By, ChromeDriver, Keys

class Website(ChromeDriver):
    def __init__(self):
        super().__init__()
```
### Finding WebElements
Arguments:
<ul>
<li>by — a selenium locator strategy </li>
<li>criteria — the search criteria to the locator strategy</li>
</ul>

```python
foo = self.element_is_present(By.TAG_NAME, "input")
```

```python
bar = self.element_is_clickable(By.XPATH, '//button[text()="bar"]')
```

### Getting Field Values
Arguments:
<ul>
<li>field — the name of the field</li>
</ul>

```python
@property
def email_address(self):
    return self.get_field_value("Email:")
```

### Pressing Keys
Arguments:
<ul>
<li>key — a selenium Keys object</li>
<li>number_of_times — the number of times to press the key</li>
</ul>

```python
self.press_key(Keys.TAB, 3)
```

### Setting Field Values
Arguments:
<ul>
<li>field — the name of the field</li>
<li>value — the value to set the field to</li>
</ul>

```python
    def login(self, username, password):
        self.set_field_value("Username:", "foo")
        self.set_field_value("Password:", "bar")
```

## Exceptions
[Selenium](https://www.selenium.dev/)'s _ElementNotInteractable_, _StaleElementReference_, and _Timeout_ exceptions can be imported from thursday as follows:
```python
from thursday.exceptions import ElementNotInteractableException, StaleElementReferenceException, TimeoutException
```

## License
[GNU General Public License (v3 only)](https://www.gnu.org/licenses/gpl-3.0.html)
