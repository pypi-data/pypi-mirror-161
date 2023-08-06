import re

from url_manager.enum import StrEnum
from url_manager.helper import compose


class TopLevelDomains(StrEnum):
    COM = "com"
    ME = "me"


def extract_valid_url(url: str) -> str:
    url_formatted = compose(
        _remove_www_from_url,
        _remove_query_params_from_url,
        _transform_http_to_https,
        _regex_to_retrieve_url,
    )(url)

    return url_formatted


def _remove_www_from_url(source_url: str) -> str:
    return source_url.replace("www.", "")


def _remove_query_params_from_url(source_url: str) -> str:
    return re.sub(r"\?.*", "", source_url)


def _transform_http_to_https(source_url: str) -> str:
    return source_url.replace("http://", "https://")


def _regex_to_retrieve_url(source_url: str) -> str:
    """
    Return an url matching these following rules:
        1 - Is http or https
        2 - All inside http://-------------.(com|me)
    """

    regex_to_retrieve_url = r"(https?://[^\s]+\.(?:{}))".format(
        "|".join(list(TopLevelDomains))
    )
    result_regex = re.findall(regex_to_retrieve_url, source_url)

    return result_regex[0] if result_regex else ""
