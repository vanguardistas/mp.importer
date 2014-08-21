from lxml import etree

BLOCK_ELEMENTS = frozenset(['p', 'h4', 'hr', 'pre', 'blockquote', 'ul', 'ol', 'li'])

# Charachters
C_NB_SPACE = b'\xa0'.decode('latin-1')

def remove_all_whitespace(text):
    if text is None:
        return text
    text = text.replace(' ', '')
    text = text.replace('\n', '')
    text = text.replace('\r', '')
    text = text.replace('\t', '')
    return text.replace(C_NB_SPACE, '')

def bubble_one_up(node):
    """Push a node up one level in the tree.

    If the parent node has content, it will be split in two."""
    parent = node.getparent()
    grandparent = parent.getparent()
    if grandparent is None:
        return
    new = etree.Element(parent.tag)
    grandparent.insert(grandparent.index(parent), new)
    new.text = parent.text
    parent.text = node.tail
    node.tail = None
    for n in parent:
        if n is node:
            break
        parent.remove(n)
        new.append(n)
    else:
        raise AssertionError('oops') # pragma: no cover
    parent.remove(node)
    grandparent.insert(grandparent.index(parent), node)
    # optionally remove either parent or new if they are empty
    if parent.text is None and not len(parent):
        node.tail = parent.tail
        grandparent.remove(parent)
    if new.text is None and not len(new):
        grandparent.remove(new)

def drop_node(node, add_padding=False, keep_content=True):
    """Remove a tag while optionally keeping the content.

    If add_passing is true, a single whitespace will be added at the start and
    end of the node's content if necessary.

    The node's tail will allways be preserved.
    """
    parent = node.getparent()
    prev = node.getprevious()
    if keep_content:
        # save the node's text
        if node.text:
            _save_text(parent, prev, node.text, add_padding)
        # save the node's children
        for child in node.getchildren():
            node.remove(child)
            if prev is None:
                parent.insert(0, child)
            else:
                parent.insert(parent.index(prev) + 1, child)
            prev = child # new last node
    # save the node's tail
    if node.tail:
        _save_text(parent, prev, node.tail, add_padding)
    parent.remove(node)


def remove_noop_inline_elements(context, content):
    """Remove inline elements that have no effect.

    For example a span with no attributes. i.e.
        <span>FooBar</span>
    """
    for node in content.findall('.//span'):
        if node.attrib:
            continue
        drop_node(node, add_padding=False, keep_content=True)

def remove_useless_br(context, content):
    """Remove <br> tags that do not contribute anything to rendering.

    It is reasonably safe to remove a br if it is the last or first node in a blocklevel element
    """
    for node in content.findall('.//br'):
        if node.text or len(node):
            # sanity checks (though br should never contain nodes or have text)
            continue
        parent = node.getparent()
        next = node.getnext()
        prev = node.getprevious()
        if next is not None and next.tag in BLOCK_ELEMENTS and not remove_all_whitespace(node.tail):
            if prev is not None:
                prev.tail = prev.tail or ''
                prev.tail += node.tail or ''
            else:
                parent.text = parent.text or ''
                parent.text += node.tail or ''
            parent.remove(node)
            context.prob('fuzzy_fix', 'remove <br/> before block element')
            continue
        if prev is not None and prev.tag in BLOCK_ELEMENTS and not remove_all_whitespace(prev.tail):
            prev.tail = prev.tail or ''
            prev.tail += node.tail or ''
            parent.remove(node)
            context.prob('fuzzy_fix', 'remove <br/> before after element')
            continue
        if node is parent[0] and not remove_all_whitespace(parent.text):
            if parent.tag in BLOCK_ELEMENTS:
                parent.text = parent.text or ''
                parent.text += node.tail or ''
                parent.remove(node)
                context.prob('fuzzy_fix', 'remove leading <br/> in block element')
                continue
            else:
                grandparent = parent.getparent()
                if not remove_all_whitespace(grandparent.text) and parent is grandparent[0]\
                        and grandparent.tag in BLOCK_ELEMENTS:
                    parent.text = parent.text or ''
                    parent.text += node.tail or ''
                    parent.remove(node)
                    context.prob('fuzzy_fix', 'remove leading <br/> in block element')
                    continue
        if node is parent[-1] and not remove_all_whitespace(node.tail):
            # if the br is the last node in the parent
            if parent.tag not in BLOCK_ELEMENTS:
                # let's look at our parent's parent, maybe that's a block tag
                # we can still remove the br if we are something like <a>text<br/></a></p>
                if remove_all_whitespace(parent.tail):
                    continue
                grandparent = parent.getparent()
                if parent is not grandparent[-1]:
                    continue
                if grandparent.tag not in BLOCK_ELEMENTS:
                    continue
            context.prob('fuzzy_fix', 'remove trailing <br/> in block element')
            parent.remove(node)
            return remove_useless_br(context, content)

#
# Internal utilities
#

def _save_text(parent, previous, text, add_space):
    if text.startswith(' '):
        add_space = False
    if previous is not None:
        # stick text onto the previou node's tail
        if not previous.tail:
            previous.tail = text
        else:
            if add_space and previous.tail[-1] != ' ':
                previous.tail += ' '
            previous.tail += text
    else:
        # no previous node, stick our tail onto the parent's text
        if not parent.text:
            parent.text = text
        else:
            if add_space and parent.text[-1] != ' ':
                parent.text += ' '
            parent.text += text

