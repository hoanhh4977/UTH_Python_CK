from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    # Kiểu tra có phải 1 url hợp lệ hay không
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
