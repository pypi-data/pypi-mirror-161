from datetime import datetime
from pathlib import Path
from typing import Iterable

import yaml

from .consts import APISection, APIText, APITranslation, Attribute, Text


class CacheMiss(Exception):
    pass


class Cache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir

    def _get_cache_path(self, search: Iterable[str], lang1: str, lang2: str) -> Path:
        return self.cache_dir / lang2 / lang1 / f'{"#".join(search)}.yml'

    def lookup(self, search: Iterable[str], lang1: str, lang2: str):
        cache_path = self._get_cache_path(search=search, lang1=lang1, lang2=lang2)

        if not cache_path.is_file():
            raise CacheMiss

        with cache_path.open("r") as file:
            cache_entry = yaml.safe_load(file)

        if cache_entry["cache_format"] != "v1":
            raise CacheMiss

        ret = list[APISection]()

        for serialized_section in cache_entry["data"]:
            section = APISection()

            for serialized_translation in serialized_section:
                translation = list[APIText]()

                for serialized_lang_text in serialized_translation:
                    lang_text = APIText()

                    for [tag_name, tag_value] in serialized_lang_text:
                        if tag_name == "Text":
                            lang_text.append(Text(tag_value))
                        elif tag_name == "Attribute":
                            lang_text.append(Attribute(tag_value))
                    translation.append(lang_text)
                section.append(APITranslation(translation))
            ret.append(section)

        cache_entry["last_used"] = int(datetime.now().timestamp())
        cache_entry["num_used"] = int(cache_entry["num_used"]) + 1

        with cache_path.open("w") as file:
            yaml.safe_dump(cache_entry, file)

        return ret

    def store(
        self,
        search: Iterable[str],
        lang1: str,
        lang2: str,
        data: list[APISection],
    ):
        cache_path = self._get_cache_path(search=search, lang1=lang1, lang2=lang2)
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        cache_entry = {
            "last_used": int(datetime.now().timestamp()),
            "num_used": 1,
            "cache_format": "v1",
            "data": [],
        }

        for section in data:
            serialized_section = []

            for translation in section:
                serialized_translation = []

                for lang_text in translation:
                    serialized_lang_text = []

                    for tag in lang_text:
                        serialized_lang_text.append(
                            [
                                tag.__class__.__name__,
                                str(tag),
                            ]
                        )
                    serialized_translation.append(serialized_lang_text)
                serialized_section.append(serialized_translation)
            cache_entry["data"].append(serialized_section)
        with cache_path.open("w") as file:
            yaml.safe_dump(cache_entry, file)
