# -*- coding: utf-8 -*-

import pkgutil

import icu

_trans = icu.Transliterator.createInstance('Any-Latin; Latin-ASCII')
t
def _load_stopwords(language):
    """Load a list of stopwords from a file.

    file must be lowercased and already in ascii form."""
    data = pkgutil.get_data('mp.importer', 'stopwords/{}.txt'.format(language))
    data = data.decode('utf-8')
    data = [d.strip() for d in data.split()]
    data = [_trans.transliterate(d) for d in data if d]
    return set(data)

_STOPWORDS = {
        'en': _load_stopwords('en'),
        'de': _load_stopwords('de'),
        'es': _load_stopwords('es'),
        }

def _remove_stopwords(txt, language='en'):
    stopwords = _STOPWORDS.get(language)
    if stopwords is not None:
        words = txt.split(' ')
        words = [w for w in words if w not in stopwords]
        txt = ' '.join(words)
    return txt

def urlname_suggester(txt, language='en'):
    """Convert any unicode string to a "safe" urlname.

    If conversion results in an empty string, the original string will be returned
    """
    ascii_txt = _trans.transliterate(txt)
    ascii_txt = ascii_txt.lower()
    ascii_txt = _remove_stopwords(ascii_txt, language=language)
    # replace anything that is not a n unreserved char with a -
    # https://tools.ietf.org/html/rfc3986#section-2.3
    urlname = []
    prev = ''
    for i in ascii_txt:
        if i not in "abcdefghijklmnopqrstuvwxyz0123456789-_.~":
            i = '-'
        if prev == '-' and i == '-':
            continue
        urlname.append(i)
        prev = i
    while len(urlname) > 1 and urlname[0] == '-':
        urlname.pop(0)
    while len(urlname) > 1 and urlname[-1] == '-':
        urlname.pop(-1)
    if not urlname:
        # failsafe, we removed everything!
        return txt
    return ''.join(urlname)
