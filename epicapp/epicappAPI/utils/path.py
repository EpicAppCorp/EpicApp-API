from ..config import HOST


def get_path_id(url_string):
    url_comps = url_string.split('/')
    # remove trailing slash
    if url_comps[-1] == '/':
        url_comps.pop()
    return url_comps[-1]


def get_url_id(id):
    return f"{HOST}/api/authors/{id}"
