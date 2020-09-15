# Selenium Integrations for Questions Three

This document assumes you are familiar with both [Questions Three](https://github.com/CyberGRX/questions-three) and [Selenium WebDriver](https://selenium.dev/documentation/en/webdriver/) and are interested in putting them together to build beautiful Web UI checks.

### Features
- Extended WebDriver class (`Browser`)
  - [Does everything that WebDriver can](#webdriver-pass-through)
  - [Automatically publishes a screen shot and a DOM dump for each test failure](#artifact-publishing)
  - [Provides extra "find" methods with a more pythonic syntax](#extra-find-methods)
  - [Can place artifacts in local (HTML 5) storage](#local-storage)
  - [Can detect navigation to a new page](#detect-new-page)
  - [Waterproof, as used in hospitals](https://www.youtube.com/watch?v=WzAB0P5KFyY)


- Support for remote browsers
  - [BrowserStack](#browserstack-support)
  - [Selenium Grid](#grid-support)


## A trivial example
This example assumes that you have Chrome and [Chromedriver](https://chromedriver.chromium.org/) installed locally.  Chrome is the default browser but Firefox is also supported.  See [Controlling behavior with environment variables](#general-environment-variables).

```
pip install questions-three-selenium
```

trivial_example.py
```
from expects import expect, contain
from questions_three.scaffolds.test_script import test, test_suite
from questions_three_selenium.browser.browser import Browser

with test_suite('SeleniumExample'):

    browser = Browser()
    browser.get('http://www.example.com')

    # This test will probably pass
    with test('Verify text contains example domain'):
        html = browser.find_unique_element(tag_name='html')
        expect(html.text.lower()).to(contain('example domain'))

    # This test should fail unless the Spinach Inquisition takes over example.com
    with test('Verify text contains Cardinal Biggles'):
        html = browser.find_unique_element(tag_name='html')
        expect(html.text.lower()).to(contain('Cardinal Biggles'))

```

```
python3 trivial_example.py
```

The example includes a failing case so you can inspect the `reports` directory and see the artifacts that get saved when something fails.


<a name="general-environment-variables"><h2>Controlling behavior with environment variables</h2></a>

**BROWSER_LOCATION**
- Set this to "local" to use a local browser
- Set it to "browserstack" to use a remote browser via BrowserStack
- Set it to "selenium_grid" to use a remote browser via Selenium Grid

**USE_BROWSER**
- Set this to "chrome" to use Chrome
- Set it to "firefox" to use Firefox

**USE_BROWSER_VERSION**
- Request this version of the browser.  Applies only to remotes.

**CHROME_USER_AGENT**
- If using Chrome, pretend to be some other browser by hacking the user agent string to this.

**BROWSER_AVAILABILITY_TIMEOUT**
- Wait up to this number of seconds for a browser to become available

**BROWSER_ELEMENT_FIND_TIMEOUT**
- Wait up to this number of seconds for a requested element to appear in the DOM

**SUPPRESS_BROWSER_EXIT_ON_FAILURE**
- Ordinarily, the browser will close automatically when the test suite ends.  Set this to "true" to leave the browser open after something breaks.  Useful for debugging.


## Browser objects
The trivial example launches a web browser by instantiating a `Browser` object.  `Browser` is mostly a wrapper around `selenium.webdriver.[browser name].webdriver.WebDriver`.

<a name="webdriver-pass-through"><h3>It can behave like an ordinary WebDriver object</h3>
</a>
`Browser` objects can do anything that the underlying `WebDriver` can do, as documented in [Selenium with Python](https://selenium-python.readthedocs.io/).

Here is the simple example from the Selenium documentation, modified to use `Browser`:
```
from questions_three_selenium import Browser
from selenium.webdriver.common.keys import Keys

driver = Browser()
driver.get("http://www.python.org")
assert "Python" in driver.title
elem = driver.find_element_by_name("q")
elem.clear()
elem.send_keys("pycon")
elem.send_keys(Keys.RETURN)
assert "No results found." not in driver.page_source
driver.close()
```

The example calls `driver.close()` but, when you instantiate a `Browser` inside a Questions Three suite, it will close automatically after the suite ends.

<a name="artifact-publishing"><h3>Artifact publishing</h3></a>

`Browser` is capable of producing a screen shot or a DOM dump (human-readable HTML file that shows all elements in the DOM at some point in time).

#### Manual generation

Most of the time, you won't need to do this because `Browser` automatically publishes artifacts when a failure occurs, but it's possible:

```
from questions_three_selenium.dom_dumper.dump_dom import dump_dom

browser = Browser()
browser.get('http://www.example.com/')

html_string = dump_dom(browser)
screenshot_png_bytes = browser.get_screenshot_as_png()
# Use your imagination.  Do something creative with your artifacts.
```

#### Automatic publishing

Bottom line: you'll see a DOM dump and a screen shot in the `reports` directory for each test that fails.  Read on if you would like to understand how this works.

At its core, Questions Three is [event-driven](https://en.wikipedia.org/wiki/Event-driven_architecture).  When something goes wrong, the scaffold publishes the appropriate event (`SUITE_ERRED`, `TEST_ERRED`, or `TEST_FAILED`). `Browser` subscribes to all three. When any of these events occurs, it does the following:
1. Take a screen shot of itself
1. Publish the screen shot as an `ARTIFACT_CREATED` event
1. Take a DOM dump of itself
1. Publish the DOM dump as an `ARTIFACT_CREATED` event

By default, Questions Three activates a reporter called `ArtifactSaver`.  It subscribes to `ARTIFACT_CREATED` events and saves each artifact to the appropriate place under `reports`.


<a name="extra-find-methods"><h3>Extra find methods</h3></a>
a `Browser` instance can be used just like an ordinary `WebDriver` instance.  For the sake of convenience and readability, it offers alternative methods for finding elements.

### pythonic syntax
The extra methods accept locators as keyword arguments, so instead of this

```
browser.find_elements(By.LINK_TEXT, 'Finland')
```

you can write this:

```
browser.find_all_matching_elements(link_text='Finland')
```

All selectors defined by `selenium.webdriver.common.by` are supported.

### find_all_matching_elements
Returns a list of all elements that match the given keyword.  If no elements match, returns an empty list.

```
divs = browser.find_all_matching_elements(tag_name='div')
bobs = browser.find_all_matching_elements(id='bob')
```

### find_unique_element
Expects the given keyword argument to match exactly one element in the DOM.
If the expectation is met, returns the element.
If if no element matches, raises NoSuchElement.
If more than one element matches, raises TooManyElements.

```
great_sorcerer = browser.find_unique_element(id='tim?')
```

<a name="detect-new-page"><h3>Detecting navigation to a new page</h3></a>

```
from questions_three.vanilla import wait_for
from questions_three_selenium import Browser

browser = Browser()
browser.get('http://www.example.com/magic_page')
are_we_there_yet = browser.func_that_detects_new_page()
browser.find_unique_element(id='magic_button').click()
wait_for(are_we_there_yet, timeout=20, throttle=1)
```

<a name="local-storage"><h3>Writing to HTML 5 local storage</h3></a>

Some web applications use [local storage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage) instead of cookies for storing things like session tokens.  `Browser` provides a convenience method for writing to it.

```
session = log_in(username='ximinez', password='N0b0dyExpects')
browser.add_to_local_storage(key='session_token', value=session)
```

<a name="browserstack-support"><h3>BrowserStack support</h3></a>

Tying `Browser` to a fresh remote browser from [BrowserStack](https://www.browserstack.com) is a simple matter of setting some environment variables -- unless you also want to use their ["Local"](https://www.browserstack.com/local-testing) tunnel.  More on that in a bit.

For best results, visit BrowserStack's [Capabilities](https://www.browserstack.com/automate/capabilities) page and play with the available configurations.  Each of the capabilities maps to an environment variable for Questions Three Selenium:

| Capability      | Environment Variable Name|
|---------------- |--------------------------|
| os              | BROWSERSTACK_OS          |
| os_version      | BROWSERSTACK_OS_VERSION  |
| browser         | USE_BROWSER              |
| browser_version | USE_BROWSER_VERSION      |

Other required environment variables:
- BROWSER_LOCATION
  - Set this to "browserstack"
- BROWSERSTACK_USERNAME
  - Set this to the username associated with the BrowserStack account
- BROWSERSTACK_ACCESS_KEY
  - Set this to the access key provided by BrowserStack for automation

Optional environment variables:
- BROWSERSTACK_SCREEN_RESOLUTION
  - Set this to one of the strings under "resolution" on the [Capabilities page](https://www.browserstack.com/automate/capabilities)
- BROWSERSTACK_SET_DEBUG
  - Set this to "true" or "false."  It defaults to "false."

With those environment variables set, instantiate a `Browser` object as normal and it will launch a remote browser via BrowserStack.


### "Local" tunnel

The tunnel requires an executable binary provided by BrowserStack. The BrowserStack integration expects this binary to be in a zip archive at some URL.  For best performance, this URL should refer to a nearby location that you control.

Required environment variables:
- BROWSERSTACK_SET_LOCAL
  - Set this to "true"
- BROWSERSTACK_LOCAL_BINARY_ZIP_URL
  - This defaults to the Linux x64 binary at BrowserStack.  Point it to wherever you have a zip archive of the binary.
- BROWSERSTACK_LOCAL_BINARY
  - Full path and filename to where the binary should be stored locally.  Default: `/tmp/browserstack_tunnel/BrowserStackLocal`
- BROWSERSTACK_URL
  - URL to the BrowserStack hub. Default: `http://hub.browserstack.com/wd/hub`

Optional environment variables:
- BROWSERSTACK_TUNNEL_TIMEOUT
  - Wait up to this number of seconds for the tunnel to open. Default: 30.


<a name="grid-support"><h3>Selenium Grid support</h3></a>

[Selenium Grid](https://selenium.dev/documentation/en/grid/) support is a simple matter of setting environment variables and then instantiating a `Browser` object normally.

Required environment variables:
- BROWSER_LOCATION
  - Set this to "selenium_grid"
- USE_BROWSER
  - Set this to the name of the expected browser (e.g. "Firefox").  The exact names will vary with Grid configuration.
- SELENIUM_GRID_HUB_URL
  - Set this to the URL of your hub

Optional environment variables:
- USE_BROWSER_VERSION

## Authoritative list of environment variables
See [module_cfg.yml](questions_three_selenium/module_cfg.yml)
