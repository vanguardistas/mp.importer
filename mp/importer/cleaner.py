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

def remove_useless_br(context, content):
    # remove a br if it is the last node in a blocklevel element and has a whitespace tail
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
