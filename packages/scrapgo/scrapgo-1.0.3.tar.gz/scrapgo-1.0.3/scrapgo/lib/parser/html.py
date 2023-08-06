from bs4.element import Tag



def prettier(content):
    if not isinstance(content, (str, Tag, bytes)):
        return content

    if isinstance(content, Tag):
        content = content.get_text(strip=True)
        
    trantab = {
        '<br>': '',
        '</br>': '\n',
        '<p>':'',
        '</p>': '\n',
        '\t': '',
        '\u200b': '',
        '\xa0': '',
        
    }

    for tok, repl in trantab.items():
        content = content.replace(tok, repl)
    
    lines = []
    for line in content.split('\n'):
        if line := line.strip():
            lines.append(line)
    return '\n'.join(lines)




def get_nested_soup_depth(soup, *args, max_depth=True, **kwargs):
    def counter(soup, count=0):
        for e in soup(*args, **kwargs):
            yield from counter(e, count+1)
        yield count
    if max_depth:
        return max(counter(soup))
    return min(counter(soup))



def filter_nested_soup_by_depth(soup, *args, depth=0, **kwargs):
    return [
        e for e in soup(*args, **kwargs)
        if get_nested_soup_depth(e, *args, **kwargs) == depth
    ]


def find_table(soup:Tag, *columns:str, tag_name='table'):
    def filter(tag):
        if tag.name != tag_name:
            return False
        for col in columns:
            if col not in tag.text:
                return False
        return True
    depth = get_nested_soup_depth(soup, filter, max_depth=False)
    if tables := filter_nested_soup_by_depth(soup, filter, depth=depth):
        return tables[0]


def load_form_values(soup:Tag, selector, value_field='value', fill_value=None):
    return {
        input['name']: input.get(value_field, fill_value)
        for input in soup.select_one(selector).select('[name]')
    }
        
