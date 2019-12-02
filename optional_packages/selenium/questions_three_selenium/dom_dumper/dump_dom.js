RECURSION_LIMIT = 30;

COMMENT_NODE = 8;


function parseAttributes(attributes) {
  var parsed = {};
  if (attributes) {
    for (var n=0; n < attributes.length; n++) {
      attrs = attributes[n];
      parsed[attrs.name] = attrs.value;
    }
  }
  return parsed;
}

function parseChildren(childNodes, depth) {
  var parsed = [];
    if (childNodes) {
      for (var i=0; i < childNodes.length; i++) {
        parsed.push(parseNode(childNodes[i], depth));
      }
    }
  return parsed;
}

function parseNode(node, depth) {

  var parsed = {
      'attributes': {},
      'children': []
  };

  if (depth > RECURSION_LIMIT) {
    parsed.type = COMMENT_NODE;
    parsed.name = '#comment';
    parsed.value = 'WARNING: DOM recursion limit reached';
  }
  else {
    parsed.type = node.nodeType;
    parsed.name = node.nodeName;
    parsed.value = node.nodeValue;
    parsed.attributes = parseAttributes(node.attributes);
    parsed.children = parseChildren(node.childNodes, depth+1);
  }
  return parsed;
}

return parseNode(document, 0);
