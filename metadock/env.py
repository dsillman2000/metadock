import abc
import itertools
from typing import Annotated, Any, Iterable


def _is_nonstr_iter(item: Any):
    try:
        iter(item)
        return not isinstance(item, str)
    except TypeError:
        return False


class MetadockNamespace(abc.ABC):
    exports: list[str] = []
    namespaces: list[str] = []
    filters: list[Annotated[str, "endswith('_filter')"]] = []

    def dict(self):
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

    def __getattr__(self, name: str):
        if name in self.exports + ["__class__"]:
            return super().__getattribute__(name)
        else:
            raise AttributeError(f"Namespace {self.__class__.__name__} has no attribute {name}, or does not export it.")
            return super().__getattribute__(name)


class MetadockMdNamespace:
    exports = ["blockquote", "code", "codeblock", "list", "tablehead", "tabelrow"]
    filters = ["list"]

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
            header_cells = tuple(f"<b>{cell}</b>" for cell in header_cells)
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

    def list_filter(self, values: Iterable[str]):
        if _is_nonstr_iter(values):
            return self.list(*values)
        assert isinstance(values, str)
        return self.list(values)


class MetadockEnv(MetadockNamespace):
    md = MetadockMdNamespace()
    exports = ["debug"]
    namespaces = ["md"]
    filters = ["chain", "with_prefix", "with_suffix", "zip"]

    def debug(self, message: str):
        print(message)
        return ""

    def chain_filter(self, values: Iterable[Iterable[Any]]):
        return itertools.chain.from_iterable(values)

    def listify_filter(self, values: Iterable[str], namespace: MetadockNamespace):
        return list(map(getattr(namespace, "list"), values))

    def with_prefix_filter(self, value: str, prefix: str, sep: str = ""):
        return sep.join((prefix, value))

    def with_suffix_filter(self, value: str, suffix: str, sep: str = ""):
        return sep.join((value, suffix))

    def zip_filter(self, *iterables):
        return zip(*iterables)
