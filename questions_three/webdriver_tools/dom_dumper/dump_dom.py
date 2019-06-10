import sys

from questions_three.vanilla import module_filename


def get_script():
    script_filename = module_filename(
        module=sys.modules[__name__], filename='dump_dom.js')
    with open(script_filename, 'r') as f:
        return f.read()


def dump_element(element):
    html = '<div>'
    html += '<b>%s</b> %s' % (element['name'], element['attributes'])
    if element['value']:
        html += '<p>%s</p>' % element['value']
    if element['children']:
        html += '<ul>'
        for child in element['children']:
            html += '<li>%s</li>' % dump_element(child)
        html += '</ul>'
    html += '</div>'
    return html


def dump_dom(driver):
    """
    Dump the DOM for the current page as an HTML string.

    driver -- (webdriver)
    """
    root = driver.execute_script(get_script())
    return '<html><body>%s</body></html>' % dump_element(root)
