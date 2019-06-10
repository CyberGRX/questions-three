
# Questions-Three
### A Library for Serious Software Interrogators (and silly ones too)

> Stop! Who would cross the Bridge of Death must answer me these questions three, ere the other side he see.
>
-- The Keeper

## Why you want this
The vast majority of support for automated software testing falls into two main groups: low-level unit testing tools that guide design and maintain control over code as it is being written, and high-level system testing tools that reduce the workload of human testers after the units have been integrated.  

The first group is optimized for precision and speed.  A good unit test proves exactly one point in milliseconds.  The second group is optimized for efficient use of human resources, enabling testers to repeat tedious actions without demanding much (or any) coding effort.

Engineering is all about trade-offs.  We can reduce the coding effort, but only if we are willing to sacrifice control.   This makes the existing high-level test automation tools distinctly unsatisfactory to testers who would prefer the opposite trade: more control in exchange for the need to approach automation as a _bona-fide_ software development project.

**If you want complete control over your system-level automated tests and are willing to get some coding dirt under your fingernails in exchange, then Questions-Three could be your best friend.**  As a flexible library rather than an opinionated framework, it will support you without dictating structures or rules.  Its features were designed to work together, but you can use them separately or even integrate them into the third-party or homegrown framework of your choice.

## What's in the Box

 - **Scaffolds** that help you structure your tests.  Chose one from the library or use them as examples to build your own.

 - **Reporters** that provide results as expected by various readers.  Use as many or as few as you would like, or follow the design pattern and build your own.

 - **Event Broker** which allows components to work together without knowing about one another.  Need to integrate a new kind of reporter?  Simply contact the broker and subscribe to relevant events.  No need to touch anything else.

 - **HTTP Client** that tracks its own activity and converts failures to meaningful artifacts for test reports.

 - **Webdriver Integrations** that facilitate compatibility testing and make Selenium WebDriver a full citizen of Question-Three's event-driven world.

 - **Vanilla Functions** useful for testing and entirely self-contained.   Use as many or as few as you would like.

The provided "test script" scaffold helps you write a test suite which contains one or more tests.  

### Install questions-three
```
pip install questions-three
```

### Write the test
```
from questions_three.scaffolds.test_script import test, test_suite

with test_suite('ExampleSuite'):

  with test('A passing test'):
      assert True, 'That was easy'
```

### Run the test
No special executors are required.  Just run the script:
```
python example_suite.py
```

### Review the results
The console output should look like this:
```
2018-08-13 14:52:55,725 INFO from questions_three.reporters.event_logger.event_logger: Suite "ExampleSuite" started
2018-08-13 14:52:55,726 INFO from questions_three.reporters.event_logger.event_logger: Test "A passing test" started
2018-08-13 14:52:55,726 INFO from questions_three.reporters.event_logger.event_logger: Test "A passing test" ended
2018-08-13 14:52:55,729 INFO from questions_three.reporters.event_logger.event_logger: Suite "ExampleSuite" ended
```

There should also be a reports directory which contains a report:
```
> ls reports
ExampleSuite.xml    jenkins_status
```
ExampleSuite.xml is a report in the _JUnit XML_ format that can be consumed by many report parsers, including Jenkins CI.  It gets produced by the junit_reporter module.

jenkins_status is a plain text file that aggregates the results of all test suites from a batch into a single result which Jenkins can display.   It gets produced by the jenkins_build_status module.
