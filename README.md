
# Questions Three
### A Library for Serious Software Interrogators (and silly ones too)

> Stop! Who would cross the Bridge of Death must answer me these questions three, ere the other side he see.
>
-- The Keeper


## Why you want this
The vast majority of support for automated <a href="#heretical-terminology">software checking</a> falls into two main groups: low-level unit checking tools that guide design and maintain control over code as it is being written, and <a href="https://medium.com/better-programming/waiter-theres-a-database-in-my-unit-test-9698d866102e">high-level system checking</a> tools that reduce the workload of human testers after the units have been integrated.  

The first group is optimized for precision and speed.  A good unit check proves exactly one point in milliseconds.  The second group is optimized for efficient use of human resources, enabling testers to repeat tedious actions without demanding much (or any) coding effort.

Engineering is all about trade-offs.  We can reduce the coding effort, but only if we are willing to sacrifice control.   This makes the existing high-level automation tools distinctly unsatisfactory to testers who would prefer the opposite trade: more control in exchange for the need to approach automation as a _bona-fide_ software development project.

**If you want complete control over your system-level automation and are willing to get some coding dirt under your fingernails in exchange, then Questions Three could be your best friend.**  As a flexible library rather than an opinionated framework, it will support you without dictating structures or rules.  Its features were designed to work together, but you can use them separately or even integrate them into the third-party or homegrown framework of your choice.

<a name="heretical-terminology"><h2>A note on heretical terminology</h2></a>
The vast majority of software professionals refer to inspection work done by machines as "automated testing."  James Bach and Michael Bolton make <a href="https://www.satisfice.com/blog/archives/856">a strong case</a> that this is a dangerous abuse of the word "testing" and suggest that we use "checking" instead when we talk about executing a procedure with a well-defined expected outcome.

Questions Three tries to maintain neutrality in this debate.  Where practical, it lets you choose whether you want to say "test" or "check."  Internally, it uses "test" for consistency with third-party libraries.  As the public face of the project, this documentation falls on the "check" side.  It says "check suite" where most testers would say "test suite."

## Orientation Resources

- Article: <a href="https://medium.com/better-programming/waiter-theres-a-database-in-my-unit-test-9698d866102e">"Waiter, There's a _Database_ in My Unit Test!"</a> explains the differences between unit, integration, and system testing and the role for each.

- Video: <a href="https://drive.google.com/open?id=1OyRVtQtciLmLiyzwA0tUb3ActWecnenZ">"Industrial Strength Automation"</a> presentation from STARWEST 2019 makes the cases for and against building a serious automation program.  It concludes with an extended discussion on the history, purpose, and design of Questions Three.


## What's in the Box

- <a href="#scaffolds-section">**Scaffolds**</a> that help you structure your checks.  Chose one from the library or use them as examples to build your own.

- <a href="#reporters-section">**Reporters**</a> that provide results as expected by various readers.  Use as many or as few as you would like, or follow the design pattern and build your own.

 - <a href="#event-broker-section">**Event Broker**<a> which allows components to work together without knowing about one another.  Need to integrate a new kind of reporter?  Simply contact the broker and subscribe to relevant events.  No need to touch anything else.

- <a href="#http-client-section">**HTTP Client**</a> that tracks its own activity and converts failures to meaningful artifacts for test reports.

- <a href="logging-section">**Logging Subsystem**</a> that, among other things, allows you to control which modules log at which level via environment variables.

- <a href="#vanilla-section">**Vanilla Functions**</a> that you might find useful for checking and are entirely self-contained.   Use as many or as few as you would like.

- <a href="#bulk-runner-section">**Bulk Suite Runner**</a> that lets you run multiple suites in parallel and control their execution via environment variables.

## Optional Packages

  - <a href="optional_packages/aws"><b>Amazon Web Services Integrations</b></a>

  - <a href="optional_packages/selenium"><b>Selenium Integrations</b></a> that facilitate compatibility checking and make Selenium WebDriver a full citizen of Question-Three's event-driven world.

## Quick Start

### Install questions-three
```
pip install questions-three
```

### Write the suite
```
from questions_three.scaffolds.check_script import check, check_suite

with check_suite('ExampleSuite'):

  with check('A passing check'):
      assert True, 'That was easy'
```

### Run the suite
No special executors are required.  Just run the script:
```
python example_suite.py
```

### Review the results
The console output should look like this:
```
2018-08-13 14:52:55,725 INFO from questions_three.reporters.event_logger.event_logger: Suite "ExampleSuite" started
2018-08-13 14:52:55,726 INFO from questions_three.reporters.event_logger.event_logger: Check "A passing check" started
2018-08-13 14:52:55,726 INFO from questions_three.reporters.event_logger.event_logger: Check "A passing check" ended
2018-08-13 14:52:55,729 INFO from questions_three.reporters.event_logger.event_logger: Suite "ExampleSuite" ended
```

There should also be a reports directory which contains a report:
```
> ls reports
ExampleSuite.xml    jenkins_status
```
ExampleSuite.xml is a report in the _JUnit XML_ format that can be consumed by many report parsers, including Jenkins CI.  It gets produced by the junit_reporter module.

jenkins_status is a plain text file that aggregates the results of all test suites from a batch into a single result which Jenkins can display.   It gets produced by the jenkins_build_status module.

<a name="scaffolds-section"><h2>Scaffolds</h2></a>
Scaffolds provide a basic structure for your checks.  Their most important function is to publish events as your checks start, end, and fail.

### The top-to-bottom script scaffold

```
from questions_three.scaffolds.check_script import check, check_suite

with check_suite('ExampleSuite'):

  with check('A passing check'):
      assert True, 'That was easy'

  with check('A failing check'):
      assert False, 'Oops'
```

If you don't like saying "check," you can say "test" instead:

```
from questions_three.scaffolds.test_script import test, test_suite

with test_suite('ExampleSuite'):

  with test('A passing check'):
      assert True, 'That was easy'

  with test('A failing check'):
      assert False, 'Oops'
```

This code is an ordinary executable python script, so you can simply execute it normally.

```
python example_suite.py
```


### The xUnit style scaffold
As its name suggests, the xUnit scaffold implements the well-worn <a href="https://en.wikipedia.org/wiki/XUnit">xUnit pattern</a>.

```
from questions_three.scaffolds.xunit import TestSuite, skip


class MyXunitSuite(TestSuite):

    def setup_suite(self):
        """
        Perform setup that affects all tests here
        Changes to "self" will affect all tests.
        """
        print('This runs once at the start of the suite')

    def teardown_suite(self):
        print('This runs once at the end of the suite')

    def setup(self):
        """
        Perform setup for each test here.
        Changes to "self" will affect the current test only.
        """
        print('This runs before each test')

    def teardown(self):
        print('This runs after each test')

    def test_that_passes(self):
        """
        The method name is xUnit magic.
        Methods named "test..." get treated as test cases.
        """
        print('This test passes')

    def test_that_fails(self):
        print('This test fails')
        assert False, 'I failed'

    def test_that_errs(self):
        print('This test errs')
        raise RuntimeError('I tried to think but nothing happened')

    def test_that_skips(self):
        print('This test skips')
        skip("Don't do that")
```
The most important advantage of the xUnit scaffold over the script one is that it automatically repeats the same set-up and tear-down routines between `test_...` functions.  Its main disadvantage is that the suites aren't as beautiful to read.

Thanks to some metaclass hocus-pocus which you're free to gawk at by looking at the source code, this too is an ordinary Python executable file:

```
python my_xunit_suite.py
```

### Building your own scaffold
Nothing stops you from building your own scaffold.  The test_script scaffold makes a good example of the services your scaffold should provide.  The xUnit scaffold is much more difficult to understand (but more fun if you're into that sort of thing).

The key to understanding scaffold design is to understand the <a href="#event-broker-section">event-driven nature of Questions Three</a>.  Scaffolds are responsible for handling exceptions and publishing the following events:
- SUITE_STARTED
- SUITE_ERRED
- SUITE_ENDED
- TEST_SKIPPED
- TEST_STARTED
- TEST_ERRED
- TEST_FAILED
- TEST_ENDED

<a name="reporters-section"><h2>Reporters</h2></a>
In Questions Three, "reporter" is a broad term for an object that listens for an event, converts it to a message useful to someone or something and sends the message.  Built-in reporters do relatively dull things like sending events to the system log and producing the Junit XML report, but there is no reason you couldn't build a more interesting reporter that launches a Styrofoam missile at the developer who broke the build.

### Built-in reporters ###

| Name       | Events it subscribes to | what it does |
|------------|-------------------------|--------------|
| Artifact Saver | ARTIFACT_CREATED, REPORT_CREATED | Saves artifacts to the local filesystem. |
| Event Logger | all test lifecycle events | Sends messages to system log. |
| Junit Reporter | all test lifecycle events | Builds Junit XML reports and publishes them as REPORT_CREATED events. |
| Result Compiler | all test lifecycle events | Reports how many tests ran, failed, etc, and how long they took.  Publishes SUITE_RESULTS_COMPILED after SUITE_ENDED. |


### Custom reporters ###
A reporter can do anything you dream up and express as Python code. That includes interacting with external services and physical objects.  Think "when this occurs during a test run, I want that to happen."  For example, "When the suite results are compiled and contain a failure, I want a Slack message sent to the channel where the developers hang out."

#### Building a custom reporter ####
Result Compiler provides a simple example to follow. You don't have to copy the pattern it establishes, but it's an easy way to start.  The `ResultCompiler` class has one method for each event to which it subscribes.  Each method is named after the event (e.g. `on_suite_started`).  These method names are magic.  The imported `subscribe_event_handlers` function recognizes the names and subscribes each method to its respective event.  The `activate` method is mandatory.  The scaffold calls it before the suite starts. `activate` performs any initialization, most importantly subscribing to the events.

#### Installing a custom reporter ####
1. Ensure that the package containing your reporter is installed.
2. Create a text file that contains the name of the reporter class, including its module (e.g. `my_awesome_reporters.information_radiators.LavaLamp`).  This file can contain as many reporters as you would like, one per line.
3. Set the environment variable `CUSTOM_REPORTERS_FILE` to the full path and filename of your text file.


<a name="event-broker-section"><h2>Event Broker</h2></a>
The Event Broker is Questions Three's beating heart.  It's how the components communicate with one another.  If you're not in the business of building custom components and plugging them in, you won't need to think about the Event Broker.  If you are, it's all you'll need to think about.

The Event Broker is little more than a simple implementation of the <a href="https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern">Publish/Subscribe Pattern</a>.  Component A subscribes to an event by registering a function with the Event Broker.  Component B publishes the event with an optional dictionary of arbitrary properties.  The Event Broker calls the subscriber function, passing it the dictionary as keyword arguments.

An event can be any object. Internally, Questions Three limits itself to members of an enum called TestEvent.  It's defined in `questions_three.constants`.

An event property can also be any object. Property names are restricted to valid Python variable names so the Event Broker can send them as keyword arguments.

<a name="http-client-section"><h2>HTTP Client</h2></a>
The HTTP client is a wrapper around the widely-used <a href="https://requests.readthedocs.io/en/master/">requests module</a>, so it can serve as a drop-in replacement. Its job in life is to integrate `requests` into the event-driven world of Questions Three, doing things like publishing an HTTP transcript when a check fails.  It also adds a few features that you can use.  Nearly all of the documentation for `requests` applies to HttpClient as well.  There are two deviations, one significant and one somewhat obscure.

### Deviation 1: HTTP Client raises an exception when it encounters an exceptional status code ###

When the HTTP server returns an exceptional <a href="https://tools.ietf.org/html/rfc7231#section-6">status code</a> (anything in the 400 - 599 range), `requests` simply places the status code in the response as it always does and expects you to detect it.  HTTP Client, by contrast, detects the status for you and raises an `HttpError`.  There is an `HttpError` subclass for each exceptional status code defined by <a href="https://tools.ietf.org/html/rfc7231">RFC 7231</a> (plus one from <a href="https://tools.ietf.org/html/rfc2324">RFC 2324</a> just for fun), so you can be very specific with your `except` blocks.  For example:

```
from questions_three.exceptions.http_error import HttpImATeapot, HttpNotFound, HttpServerError
from questions_three.http_client import HttpClient

try:
  HttpClient().get('http://coffee.example.com')
except HttpImATeapot as e:
  # This will catch a 418 only
  # e.response is the requests.Response object returned by `requests.get`
  do_something_clever(response=e.response)
except HttpNotFound:
  # This will catch a 404 only
  do_something_sad()
except HttpServerError:
  # This will catch anything in the 500-599 range.
  do_something_silly()
```

### Deviation 2: json is not allowed as a keyword argument



`requests` allows you to write this:

```
requests.post('http://songs.example.com/', json=['spam', 'eggs', 'sausage', 'spam'])
```

HTTP Client does not support this syntax because it interferes with transcript generation.  Instead, write this:

```
HttpClient().post('http://songs.example.com/', data=json.dumps(['spam', 'eggs', 'sausage', 'spam'])
```

### New feature: simplified cookie management ###
Instead of creating a `requests.Session`, you can simply do this:

```
client = HttpClient()
client.enable_cookies()
```

The client will now save cookies sent to it by the server and return them to the server with each request.

### New feature: persistent request headers ###

This is particularly useful for maintaining an authenticated session:
```
client = HttpClient()
client.set_persistent_headers(session_id='some fake id', secret_username='bob')
```

The client will now send the specified headers to the server with each request.

### Tuning with environment variables ###
`HTTP_PROXY` This is a well-established environment variable. Set it to the URL of your proxy for plain HTTP requests.

`HTTPS_PROXY` As above.  Set this to the URL of your proxy for secure HTTP requests

`HTTPS_VERIFY_CERTS` Set this to "false" to disable verification of X.509 certificates.

`HTTP_CLIENT_SOCKET_TIMEOUT` Stop waiting for an HTTP response after this number of seconds.


<a name="logging-section"><h2>Logging Subsystem</h2></a>
Questions Three extends Python's logging system to do various things internally that won't matter to most users.  However, there's one feature that may be of interest.  You can customize how verbose/noisy any given module will be.  Most common targets are event_broker when you want to see all the events passing through and http_client when you want excruciating detail about every request and response.

```
export QUESTIONS_THREE_EVENT_BROKER_LOG_LEVEL=INFO
export QUESTIONS_THREE_HTTP_CLIENT_LOG_LEVEL=DEBUG
```

This works with any Questions Three module and any log level defined in the <a href="https://docs.python.org/3/library/logging.html">Fine Python Manual</a>.

You can make it work with your custom components too:

```
from questions_three.logging import logger_for_module

log = logger_for_module(__name__)
log.info('I feel happy!')
```


<a name="vanila-section"><h2>Vanilla Functions</h2></a>
You'll find these in `questions_three.vanilla`.  The unit tests under `tests/vanilla` provide examples of their use. <br/>

`b16encode()` Base 16 encode a string.  This is basically a hex dump.<br/>

`call_with_exception_tolerance()` Execute a function. If it raises a specific exception, wait for a given number of seconds and try again up to a given timeout<br/>

`format_exception()` Convert an exception to a human-friendly message and stack trace

`path_to_entry_script()` Return the full path and filename of the script that was called from the command line

`random_base36_string()` Return a random string of a given length. Useful for generating bogus test data.

`string_of_sequential_characters()` Return a string of letters and numbers in alphabetical order.  Useful for generating bogus but deterministic test data.

`url_append()` Replacement for `urljoin` that does not eliminate characters when slashes are present but does join an arbitrary number of parts.

`wait_for()` Pauses until the given function returns a truthy value and returns the value.  Includes a throttle and a timeout.



<a name="bulk-runner-section"><h2>Bulk Suite Runner</h2></a>
To run all suites in any directory below `./my_checks`:

```
python -m questions_three.ci.run_all my_checks
```


### Controlling execution with environment variables ###

`MAX_PARALLEL_SUITES` Run up to this number of suites in parallel.  Default is 1 (serial execution).

`REPORTS_PATH` Put reports and other artifacts in this directory.  Default: `./reports`

`RUN_ALL_TIMEOUT` After this number of seconds, terminate all running suites and return a non-zero exit code.

`TEST_RUN_ID` Attach this arbitrary string as a property to all events.  This allows reporters to discriminate one test run from another.


### Understanding events and reports
**(or the philosophy of errors, failures, and warnings)**

Questions Three follows the convention set by JUnit and draws an important distinction between error events and failure events.  This distinction flows from the scaffolds to the Event Broker to the reports.

A **failure event** occurs when a check makes a false assertion.  The simplest way to trigger one is `assert False` which Python converts to an `AssertionError` which the scaffold converts to a `TEST_FAILED` event.  The intent of the system is to produce a failure event only when there is high confidence that there is a fault in the system under test.

An **error event** occurs when some other exception gets raised (or, for whatever batty reason, something other than a check raises an `AssertionError`).  Depending on the context from which the exception was raised, the scaffold will convert it into a `SUITE_ERRED` or a `TEST_ERRED` event.  In theory, an error event should indicate a fault in the check.  In practice, the fault could be anywhere, especially if the system under test behaves in unanticipated ways.

Because of the expectation that failure events indicate faults in the checks and error events indicate faults in the system under test, the **Event Logger** reports failure events as warnings and error events as errors.  The warning indicates that the check did its job perfectly and the fault was somewhere else.  The error indicates that the fault is in the check.  Of course, real life is not so clean.

Because the distinction originated from the JUnit world, **Junit XML Reporter** has no need to perform any interpretation.  It reports failure events as failures and error events as errors.
