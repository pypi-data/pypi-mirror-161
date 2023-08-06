API = "https://dict.leo.org/dictQuery/m-vocab/{lang1}{lang2}/query.xml"
DEFAULTPARAMS = {
    "tolerMode": "nof",
    "rmWords": "off",
    "rmSearch": "on",
    "searchLoc": "0",
    "resultOrder": "basic",
    "multiwordShowSingle": "on",
    "lang": "de",
}
LANGUAGES = {
    "de": {"name": "German", "emoji": "🇩🇪"},
    "en": {"name": "English", "emoji": "🇺🇸"},
    "fr": {"name": "French", "emoji": "🇫🇷"},
    "es": {"name": "Spanish", "emoji": "🇪🇸"},
    "it": {"name": "Italian", "emoji": "🇮🇹"},
    "ch": {"name": "Chinese", "emoji": "🇨🇳"},
    "ru": {"name": "Russian", "emoji": "🇷🇺"},
    "pt": {"name": "Portuguese", "emoji": "🇵🇹"},
    "pl": {"name": "Polish", "emoji": "🇵🇱"},
}


class Text(str):
    """Represent a text node received from API."""


class Attribute(str):
    """Represent a <small> or <domain> attribute received from API."""


APITag = Text | Attribute
APIText = list[APITag]
APITranslation = tuple[APIText, APIText]
APISection = list[APITranslation]
