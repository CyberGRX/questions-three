from urllib.parse import urlencode, urljoin
from lxml import html


from .exceptions import FormNotFound, FormElementLacksAction, \
    FormElementLacksMethod


def assemble_submit_url(form_url, action):
    if action.startswith('http'):
        return action
    return urljoin(form_url, action)


class HtmlForm:

    def __init__(self, *, http_client, url, xpath):
        """
        Represents an HTML form on a Web page

        http_client -- HttpClient instance
        url -- GET this URL and expect it to contain an HTML form
        xpath -- Expect the form to be at this xpath
        """
        self.fields = {}
        self._http_client = http_client
        doc = html.fromstring(http_client.get(url).text)
        if xpath.startswith('/'):
            xpath = '.' + xpath
        forms = doc.findall(xpath)
        if not forms:
            raise FormNotFound('No form was found at the xpath')
        self._form = forms[0]
        if 'method' not in self._form.attrib.keys():
            raise FormElementLacksMethod('The form lacks a "method" attribute')
        self._method = self._form.attrib['method']
        if 'action' not in self._form.attrib.keys():
            raise FormElementLacksAction(
                'The form lacks an "action" attribute')
        self._submit_url = assemble_submit_url(
            url, self._form.attrib['action'])
        for element in self._form.findall('.//input'):
            keys = element.attrib.keys()
            if 'name' in keys and 'value' in keys:
                self.fields[element.attrib['name']] = element.attrib['value']

    def submit(self):
        func = getattr(self._http_client, self._method.lower())
        return func(
            self._submit_url,
            headers={'Content-type': 'application/x-www-form-urlencoded'},
            data=urlencode(self.fields))
