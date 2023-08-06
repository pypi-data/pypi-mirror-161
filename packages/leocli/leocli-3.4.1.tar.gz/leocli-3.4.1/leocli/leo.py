"""
leocli - a console translation script for https://dict.leo.org/ .
"""

# Copyright (c) 2012 Christian Schick
# Copyright (c) 2022 Sebastian Endres
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Optional

import requests
import termcolor
from bs4 import BeautifulSoup
from tabulate import tabulate

from . import __version__
from .cache import Cache, CacheMiss
from .conf import LeoConfig
from .consts import (
    API,
    DEFAULTPARAMS,
    LANGUAGES,
    APISection,
    APIText,
    APITranslation,
    Attribute,
    Text,
)

if TYPE_CHECKING:
    from bs4.element import Tag


try:
    import argcomplete
except ImportError:
    pass


def parse_args(conf: LeoConfig) -> argparse.Namespace:
    """
    Parse cli arguments.

    Return the parsed arguments
    """
    valid_langs = [lang for lang in LANGUAGES.keys() if lang != "de"]
    valid_langs_str = ", ".join(valid_langs)

    def parse_bool(value: str) -> bool:
        return value.lower() in {"y", "yes", "t", "true", "1"}

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "words",
        action="store",
        nargs="+",
        metavar="word",
        type=str,
        help="the words you want to translate",
    )
    parser.add_argument(
        "-l",
        "--lang",
        action="store",
        dest="lang",
        metavar="lang",
        type=str,
        choices=valid_langs,
        help=f"The languagecode to translate to or from. Default: {conf.lang}. Choices: {valid_langs_str}",
    )
    parser.add_argument(
        "-e",
        "--emojis",
        action="store",
        dest="use_emojis",
        metavar="y/n",
        type=parse_bool,
        help=(
            "Use emoji language flags for languages. Your terminal font must support this feature. Default: {conf.use_emojis}"
        ),
    )
    parser.add_argument(
        "--pager",
        action="store",
        dest="pager",
        metavar="pagercmd",
        type=str,
        help=f"The pager command to use. Default: '{conf.pager or 'None'}'. Use `--pager=` to disable the pager.",
    )
    parser.add_argument(
        "--use-cache",
        action="store",
        dest="use_cache",
        metavar="y/n",
        type=parse_bool,
        help=f"Cache results. Default: '{conf.use_cache}'",
    )
    parser.add_argument(
        "--cache-dir",
        action="store",
        dest="cache_dir",
        metavar="cache_dir",
        type=Path,
        help=f"Cache directory. Default: '{conf.cache_dir}'",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    if "argcomplete" in globals():
        argcomplete.autocomplete(parser)

    args = parser.parse_args()

    conf.update_from_args(args)

    return args


def get(
    search: Iterable[str],
    lang1: str = "en",
    lang2: str = "de",
) -> str:
    """Querie the API and returns a lists of result string pairs."""
    params = {"search": "+".join(search), "lp": f"{lang1}{lang2}"}
    params.update(DEFAULTPARAMS)
    try:
        res = requests.get(
            API.format(lang1=lang1, lang2=lang2),
            params=params,
        )
        res.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as err:
        termcolor.cprint(f"[!] {err}", color="red", file=sys.stderr)
        sys.exit(1)

    return res.text


def simplify_repr(root: "Tag") -> APIText:
    """Simplify the XML representation of a ``repr`` tag in API."""
    result: APIText = []

    for node in root:
        if node.name in ("domain", "small"):
            text = node.getText()
            if result and isinstance(result[-1], Attribute):
                result[-1] = Attribute(result[-1] + text)
            else:
                result.append(Attribute(text))
        else:
            if node.name is None:
                text = str(node)
            else:
                text = node.getText()

            if result and isinstance(result[-1], Text):
                result[-1] = Text(result[-1] + text)
            else:
                result.append(Text(text))

    return result


def parse_api(
    api_res: str,
    lang1: str = "en",
    lang2: str = "de",
) -> list[APISection]:
    """Parse the API response and return the results list."""
    content = BeautifulSoup(api_res, "xml")
    results = []

    for api_section in content.sectionlist.findAll("section"):
        if int(api_section["sctCount"]) > 0:
            section: APISection = []

            for entry in api_section.findAll("entry"):
                res0 = entry.find("side", attrs={"lang": lang1})
                res1 = entry.find("side", attrs={"lang": lang2})

                if res0 and res1:
                    res0_text = simplify_repr(res0.repr)
                    res1_text = simplify_repr(res1.repr)
                    section.append((res0_text, res1_text))

            if section:
                results.append(section)

    return results


def print_result(
    results: list[APISection],
    lang1: str,
    lang2: str,
    pager: Optional[str],
    with_emojis: bool,
) -> None:
    """Print the result to stdout."""

    def format_api_text(text: APIText, normal_is_bold: bool = False) -> str:
        return "".join(
            termcolor.colored(part, color="green")
            if isinstance(part, Attribute)
            else termcolor.colored(part, attrs=["bold"] if normal_is_bold else [])
            for part in text
        )

    def format_translation(translation: APITranslation) -> tuple[str, str]:
        return (
            format_api_text(translation[0], True),
            format_api_text(translation[1], False),
        )

    def format_section(section: APISection) -> list[tuple[str, str]]:
        return [format_translation(translation) for translation in section]

    def format_header(lang: str, with_emoji: bool = False) -> str:
        lang_name = LANGUAGES[lang]["name"]
        lang_emoji = LANGUAGES[lang]["emoji"]
        header_str = lang_name

        if with_emoji:
            header_str += " " + lang_emoji

        return termcolor.colored(header_str, attrs=["bold"])

    output = "\n\n".join(
        tabulate(
            format_section(section),
            headers=(
                format_header(lang1, with_emoji=with_emojis),
                format_header(lang2, with_emoji=with_emojis),
            ),
            #  tablefmt="presto",
            tablefmt="fancy_grid",
        )
        for section in results
    )

    if not pager:
        print(output)
    else:
        subprocess.run(
            pager.split(),
            input=output,
            check=True,
            encoding=sys.stdout.encoding,
        )


def lookup(
    search: Iterable[str],
    lang1: str,
    lang2: str,
    cache: Cache,
) -> list[APISection]:
    """Lookup a word, cache results."""
    try:
        words = cache.lookup(search=search, lang1=lang1, lang2=lang2)
        termcolor.cprint("Using result from cache", color="green", file=sys.stderr)

        return words
    except CacheMiss:
        pass

    api_res = get(search, lang1, lang2)
    words = parse_api(api_res, lang1, lang2)

    cache.store(search=search, lang1=lang1, lang2=lang2, data=words)

    return words


def main() -> None:
    """The main function."""
    conf = LeoConfig()
    args = parse_args(conf)
    cache = Cache(cache_dir=conf.cache_dir)
    # The second language must be 'de'
    lang2 = "de"
    words = lookup(
        search=args.words,
        lang1=conf.lang,
        lang2=lang2,
        cache=cache,
    )

    if words:
        print_result(
            words,
            conf.lang,
            lang2,
            pager=conf.pager,
            with_emojis=conf.use_emojis,
        )
    else:
        words_str = ", ".join(f'"{word}"' for word in args.words)
        print(
            termcolor.colored(
                f"No matches found for {words_str}.",
                color="red",
            ),
            file=sys.stderr,
        )
        sys.exit(1)
