import validators


def extract_valid_url(url: str):
    first_url = _get_first_url_if_has_more_than_one(url)
    if validators.url(first_url) is not True:
        return _change_url_to_right_pattern(first_url)
    return first_url


def _get_first_url_if_has_more_than_one(url: str):
    if _has_character(url, ","):
        return url.split(",")[0]
    if _has_character(url, ";"):
        return url.split(";")[0]
    if _has_character(url, " "):
        return url.split(" ")[0]
    return url


def _has_character(url: str, character: str):
    return url.find(character) != -1


def _change_url_to_right_pattern(url: str):
    if _is_instagram_user(url):
        url = url.replace("@", "https://www.instagram.com/")
    if not _is_valid_url(url):
        url = f"https://{url}"
    return url


def _is_instagram_user(url: str):
    return url.startswith("@")


def _is_valid_url(url):
    return url.startswith("https")
