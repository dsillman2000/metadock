import abc
import itertools
from typing import Annotated, Any, Iterable, Literal

import jinja2
import marko


def _is_nonstr_iter(item: Any) -> bool:
    """Utility method for determining if an item is an iterable which is not a string.

    Args:
        item (Any): Item to be checked

    Returns:
        bool: True if the item is an iterable which is not a string, False otherwise.
    """
    try:
        iter(item)
        return not isinstance(item, str)
    except TypeError:
        return False


class MetadockNamespace(abc.ABC):
    """Abstract base class for Metadock namespaces, which are used to group related functions and filters.

    Attributes:
        exports (list[str]): List of function names to be exported from this namespace.
        namespaces (list[str]): List of namespace names to be exported from this namespace.
        filters (list[str]): List of filter names to be exported as attributes of this namespace.
    """

    exports: list[str] = []
    namespaces: list[str] = []
    filters: list[Annotated[str, "implementation ends with('_filter')"]] = []

    def dict(self) -> dict[Literal["exports", "namespaces", "filters"], dict[str, Any]]:
        """Produces a dictionary of the exports, namespaces, and filters of this namespace in a fashion which can be
        consumed by a Jinja2 environment.

        Returns:
            dict[str, dict[str, Any]]: A dictionary of the exports, namespaces, and filters of this namespace.
        """
        return {
            "exports": {funcname: getattr(self, funcname) for funcname in self.exports},
            "filters": {filtname: getattr(self, filtname + "_filter") for filtname in self.filters}
            | {
                f"{nsname}.{filtname}": getattr(getattr(self, nsname), filtname + "_filter")
                for nsname in self.namespaces
                for filtname in getattr(self, nsname).filters
            },
            "namespaces": {nsname: getattr(self, nsname) for nsname in self.namespaces},
        }

    def jinja_environment(self) -> jinja2.Environment:
        """The Jinja environment constructed from this namespace.

        Returns:
            jinja2.Environment: The Jinja environment constructed from this namespace.
        """
        env_dict = self.dict()
        env = jinja2.Environment()
        env.globals.update(env_dict["exports"] | env_dict["namespaces"])
        env.filters.update(env_dict["filters"])
        return env


class MetadockMdNamespace(MetadockNamespace):
    exports = ["blockquote", "code", "codeblock", "list", "tablehead", "tablerow"]
    filters = ["convert", "list"]

    def blockquote(self, content: str):
        _blockquoted = content.strip().replace("\n", "\n> ")
        return f"> {_blockquoted}"

    def codeblock(self, content: str, language: str = ""):
        return f"```{language}\n{content.strip()}\n```"

    def code(self, content: str):
        return f"`{content.strip()}`"

    def tablerow(self, *cells: str):
        return "| " + " | ".join(cells) + " |"

    def tablehead(self, *header_cells: str, bold: bool = False):
        if bold:
            header_cells = tuple(MetadockHtmlNamespace().bold(cell) for cell in header_cells)
        return self.tablerow(*header_cells) + "\n" + self.tablerow(*(["---"] * len(header_cells)))

    def list(self, *items: str):
        _list_prefixes = ("-", "*", "+")

        def _is_md_list(item: str):
            return item.lstrip().startswith(_list_prefixes)

        listed_items = [list(map(str, item)) if _is_nonstr_iter(item) else [str(item)] for item in items]
        flat_items = list(itertools.chain.from_iterable(listed_items))
        indented_items = [item.replace("\n", "\n  ") for item in flat_items if isinstance(item, str)]
        return "\n".join(
            (f"- {flat_item}" if not _is_md_list(flat_item) else f"  {indented_item}")
            for flat_item, indented_item in zip(flat_items, indented_items)
        )

    def convert_filter(self, md_content: str):
        return marko.convert(md_content)

    def list_filter(self, values: Iterable[str]):
        if _is_nonstr_iter(values):
            return self.list(*values)
        return self.list(str(values))


class MetadockHtmlNamespace(MetadockNamespace):
    exports = ["bold", "code", "codeblock", "details", "italic", "summary", "underline"]

    def bold(self, content: str):
        return f"<b>{content}</b>"

    def code(self, content: str):
        return f"<code>{content}</code>"

    def codeblock(self, content: str, indent: int = 0):
        indented_content = content.replace("\n", "\n" + " " * indent)
        return f"<code>\n{indented_content}\n</code>"

    def details(self, *contents: str, indent: int = 0) -> str:
        indented_linesep_contents = "\n\n".join(contents).replace("\n", "\n" + " " * indent)
        return f"<details>\n{indented_linesep_contents}\n</details>"

    def italic(self, content: str):
        return f"<i>{content}</i>"

    def summary(self, content: str, indent: int = 0) -> str:
        indented_content = content.replace("\n", "\n" + " " * indent)
        return f"<summary>\n{indented_content}\n</summary>"

    def underline(self, content: str):
        return f"<u>{content}</u>"


class MetadockEnv(MetadockNamespace):
    md = MetadockMdNamespace()
    html = MetadockHtmlNamespace()
    exports = ["debug"]
    namespaces = ["html", "md"]
    filters = ["chain", "inline", "with_prefix", "with_suffix", "zip"]

    def debug(self, message: str):
        print(message)
        return ""

    def chain_filter(self, values: Iterable[Iterable[Any]]):
        return itertools.chain.from_iterable(values)

    def inline_filter(self, value: str) -> str:
        return value.replace("\n", " ").replace("  ", " ")

    def listify_filter(self, values: Iterable[str], namespace: MetadockNamespace):
        return list(map(getattr(namespace, "list"), values))

    def with_prefix_filter(self, value: str, prefix: str, sep: str = ""):
        return sep.join((prefix, value))

    def with_suffix_filter(self, value: str, suffix: str, sep: str = ""):
        return sep.join((value, suffix))

    def zip_filter(self, *iterables):
        return zip(*iterables)
