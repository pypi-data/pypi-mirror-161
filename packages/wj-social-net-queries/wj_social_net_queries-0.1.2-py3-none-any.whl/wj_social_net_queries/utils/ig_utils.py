def get_shortcode_from_permalink(permalink: str) -> str:
    """
    Description
    ----------
    Given a ig media link, extracts de shortcode as unique id

    """
    divided_link = permalink.split("/")
    return divided_link[-2]
