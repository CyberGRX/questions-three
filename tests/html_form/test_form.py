from unittest import TestCase, main
from urllib.parse import parse_qs, quote_plus, urlencode, urljoin

from expects import expect, be_empty, contain, equal

from twin_sister.expects_matchers import raise_ex
from questions_three.html_form import HtmlForm
import questions_three.html_form.exceptions as exceptions
from twin_sister.expects_matchers import contain_key_with_value
from twin_sister.fakes import EmptyFake


class FakeResponse(EmptyFake):
    def __init__(self, content, status_code=200):
        self.content = content
        self.text = content
        self.status_code = status_code

    def __bool__(self):
        return True


class FakeHttpClient:
    def __init__(self):
        self.get_requests = []
        self.post_requests = []
        self.put_requests = []
        self.get_responses = {}
        self.post_response = None

    def get(self, url, *args, **kwargs):
        self.get_requests.append((url, args, kwargs))
        if url in self.get_responses.keys():
            return self.get_responses[url]
        return FakeResponse("not found", status_code=404)

    def post(self, url, *args, **kwargs):
        self.post_requests.append((url, args, kwargs))
        return self.post_response or FakeResponse("nothing to see here")

    def put(self, url, *args, **kwargs):
        self.put_requests.append((url, args, kwargs))
        return FakeResponse("nothing to see here")


def extract_query(request):
    url, args, kwargs = request
    expect(kwargs.keys()).to(contain("data"))
    return parse_qs(kwargs["data"])


class TestForm(TestCase):
    def test_complains_if_form_not_found(self):
        fake = FakeHttpClient()
        url = "http://something"
        fake.get_responses[url] = FakeResponse(
            """
            <html><body><form id="wrong" action="spam" method="POST"/>
            </body></html>
            """
        )

        def attempt():
            HtmlForm(http_client=fake, url=url, xpath="//form[@name='right']")

        expect(attempt).to(raise_ex(exceptions.FormNotFound))

    def test_complains_if_method_not_specified(self):
        fake = FakeHttpClient()
        url = "http://something"
        fake.get_responses[url] = FakeResponse(
            """
            <html><body><form action="spam"/></body></html>
            """
        )

        def attempt():
            HtmlForm(http_client=fake, url=url, xpath="//form")

        expect(attempt).to(raise_ex(exceptions.FormElementLacksMethod))

    def test_uses_specified_http_method_ignoring_case(self):
        fake = FakeHttpClient()
        url = "http://something"
        fake.get_responses[url] = FakeResponse(
            """
            <html><body><form action="spam" method="pUt"/></body></html>
            """
        )
        form = HtmlForm(http_client=fake, url=url, xpath="//form")
        form.submit()
        expect(fake.put_requests).not_to(be_empty)

    def test_complains_if_action_not_specified(self):
        fake = FakeHttpClient()
        url = "http://something"
        fake.get_responses[url] = FakeResponse(
            """
            <html><body><form method="pUt"/></body></html>
            """
        )

        def attempt():
            HtmlForm(http_client=fake, url=url, xpath="//form")

        expect(attempt).to(raise_ex(exceptions.FormElementLacksAction))

    def test_handles_absolute_action_url(self):
        action = "http://go.net/somewhere/warm"
        fake = FakeHttpClient()
        url = "http://something"
        fake.get_responses[url] = FakeResponse(
            """
            <html><body><form action="%s" method="POST"/></body></html>
            """
            % action
        )
        form = HtmlForm(http_client=fake, url=url, xpath="//form")
        form.submit()
        actual, args, kwargs = fake.post_requests[-1]
        expect(actual).to(equal(action))

    def test_handles_action_path_with_leading_slash(self):
        action = "/the/primrose/path"
        fake = FakeHttpClient()
        scheme_and_host = "https://std.io"
        url = "%s/yogurt?things=stuff" % scheme_and_host
        fake.get_responses[url] = FakeResponse(
            """
            <html><body><form action="%s" method="POST"/></body></html>
            """
            % action
        )
        form = HtmlForm(http_client=fake, url=url, xpath="//form")
        form.submit()
        actual, args, kwargs = fake.post_requests[-1]
        expect(actual).to(equal(urljoin(scheme_and_host, action)))

    def test_handles_action_path_without_leading_slash(self):
        action = "form-processor/lives.here"
        fake = FakeHttpClient()
        scheme_and_host = "https://std.io"
        path = "parent-directory/generator"
        url = "%s/%s?things=stuff" % (scheme_and_host, path)
        fake.get_responses[url] = FakeResponse(
            """
            <html><body><form action="%s" method="POST"/></body></html>
            """
            % action
        )
        form = HtmlForm(http_client=fake, url=url, xpath="//form")
        form.submit()
        actual, args, kwargs = fake.post_requests[-1]
        expect(actual).to(equal(urljoin(urljoin(scheme_and_host, path), action)))

    def test_sends_data_set_for_existing_field(self):
        fake = FakeHttpClient()
        url = "http://yadda.dada"
        field_name = "dinks"
        value = "aargamuffin"
        fake.get_responses[url] = FakeResponse(
            """
            <html><body>
                <form action="spam" method="POST">
                    <input type="text" name="%s"/>
                </form>
            </body></html>
            """
            % field_name
        )
        form = HtmlForm(http_client=fake, url=url, xpath="//form")
        form.fields[field_name] = value
        form.submit()
        fields = extract_query(fake.post_requests[-1])
        expect(fields).to(contain_key_with_value(field_name, [value]))

    def test_sends_data_for_non_existing_field(self):
        fake = FakeHttpClient()
        url = "http://yadda.dada"
        field_name = "dinks"
        value = "aargamuffin"
        fake.get_responses[url] = FakeResponse(
            """
            <html><body>
                <form action="spam" method="POST">
                    <input type="text" name="something-else"/>
                </form>
            </body></html>
            """
        )
        form = HtmlForm(http_client=fake, url=url, xpath="//form")
        form.fields[field_name] = value
        form.submit()
        fields = extract_query(fake.post_requests[-1])
        expect(fields).to(contain_key_with_value(field_name, [value]))

    def test_sends_data_for_hidden_field(self):
        fake = FakeHttpClient()
        url = "http://yadda.dada"
        field_name = "taunt"
        value = "Your mother was a hamster"
        fake.get_responses[url] = FakeResponse(
            """
            <html><body>
                <form action="spam" method="POST">
                    <div><input type="hidden" name="%s" value="%s"/></div>
                </form>
            </body></html>
            """
            % (field_name, value)
        )
        form = HtmlForm(http_client=fake, url=url, xpath="//form")
        form.submit()
        fields = extract_query(fake.post_requests[-1])
        expect(fields).to(contain_key_with_value(field_name, [value]))

    def test_sends_data_for_other_populated_input_field(self):
        fake = FakeHttpClient()
        url = "http://yadda.dada"
        field_name = "taunt"
        value = "Your father smelled of elderberries"
        fake.get_responses[url] = FakeResponse(
            """
            <html><body>
                <form action="spam" method="POST">
                    <div><input type="spam" name="%s" value="%s"/></div>
                </form>
            </body></html>
            """
            % (field_name, value)
        )
        form = HtmlForm(http_client=fake, url=url, xpath="//form")
        form.submit()
        fields = extract_query(fake.post_requests[-1])
        expect(fields).to(contain_key_with_value(field_name, [value]))

    def test_ignores_elements_outside_specified_form(self):
        fake = FakeHttpClient()
        url = "http://yadda.dada"
        field_name = "taunt"
        fake.get_responses[url] = FakeResponse(
            """
            <html><body>
                <form action="spam" method="POST"/>
                <input type="hidden" name="%s" value="oops"/>
            </body></html>
            """
            % field_name
        )
        form = HtmlForm(http_client=fake, url=url, xpath="//form")
        form.submit()
        fields = extract_query(fake.post_requests[-1])
        expect(fields.keys()).not_to(contain(field_name))

    def test_sends_content_type(self):
        fake = FakeHttpClient()
        url = "http://yadda.dada"
        fake.get_responses[url] = FakeResponse(
            """
            <html><body><form action="spam" method="POST"/></body></html>
            """
        )
        form = HtmlForm(http_client=fake, url=url, xpath="//form")
        form.submit()
        _, args, kwargs = fake.post_requests[-1]
        expect(kwargs.keys()).to(contain("headers"))
        expect(kwargs["headers"]).to(contain_key_with_value("Content-type", "application/x-www-form-urlencoded"))

    def test_urlencodes_payload(self):
        fake = FakeHttpClient()
        url = "http://yadda.dada"
        fake.get_responses[url] = FakeResponse(
            """
            <html><body>
                <form action="spam" method="POST"/>
            </body></html>
            """
        )
        form = HtmlForm(http_client=fake, url=url, xpath="//form")
        field_name = "bad-things"
        value = "Things that don't belong in a URL: \\/!@#$%^&*()<>,}{\"?"
        form.fields[field_name] = value
        form.submit()
        _, args, kwargs = fake.post_requests[-1]
        expect(kwargs.keys()).to(contain("data"))
        expect(kwargs["data"]).to(equal(urlencode({field_name: value}, quote_via=quote_plus)))

    def test_returns_response(self):
        fake = FakeHttpClient()
        url = "http://yadda.dada"
        fake.get_responses[url] = FakeResponse(
            """
            <html><body>
                <form action="spam" method="POST"/>
            </body></html>
            """
        )
        form = HtmlForm(http_client=fake, url=url, xpath="//form")
        response = FakeResponse("winner!")
        fake.post_response = response
        expect(form.submit()).to(equal(response))


if "__main__" == __name__:
    main()
