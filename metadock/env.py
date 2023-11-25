import abc
import html
import itertools
from typing import Annotated, Any, Iterable, Literal, Sequence

import jinja2
from marko.ext.gfm import gfm


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
    """Jinja Namespace for Markdown-related functions and filters.

    **Macros**:

        blockquote
        code
        codeblock
        list
        tablehead
        tablerow

    **Filters**:

        convert
        list
    """

    exports = ["blockquote", "code", "codeblock", "list", "tablehead", "tablerow"]
    filters = ["convert", "list"]

    def blockquote(self, content: str) -> str:
        """Produces a Markdown blockquote from the given content by prepending each line with a gt symbol ("> ").

        Args:
            content (str): The content of the blockquote.

        Returns:
            str: The Markdown blockquote.
        """
        _blockquoted = content.strip().replace("\n", "\n> ")
        return f"> {_blockquoted}"

    def code(self, content: str) -> str:
        """Produces a Markdown inline code block from the given content by wrapping the string in graves ("`").

        Args:
            content (str): The content of the inline code block.

        Returns:
            str: The Markdown inline code block.
        """
        return f"`{content.strip()}`"

    def codeblock(self, content: str, language: str = "") -> str:
        """Produces a Markdown codeblock from the given content by wrapping the string in triple-graves ("```"),
        and optionally specifies a language.

        Args:
            content (str): The content of the codeblock.
            language (str, optional): Language attribute for the code block. Defaults to empty string.

        Returns:
            str: The Markdown codeblock.
        """
        return f"```{language}\n{content.strip()}\n```"

    def list(self, *items: str) -> str:
        """Produces a Markdown list from the given content by prepending each line with a dash ("- "). If any of its
        arguments are, themselves, formatted as Markdown lists, then they are simply indented as sublists.

        Args:
            *items (str): The individual items and/or sub-lists which compose the list.

        Returns:
            str: The composite Markdown list.
        """
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

    def tablerow(self, *cells: str) -> str:
        """Produces a Markdown table row from the given cells by joining each cell with pipes ("|") and wrapping the
        result in pipes. Cell contents have their pipes escaped with a backslash ("\\").

        Args:
            *cells (str): The cells of the table row.

        Returns:
            str: The Markdown table row.
        """
        _pipe_escaped_cells = tuple(map(lambda cell: cell.replace("|", "\\|"), cells))
        return "| " + " | ".join(_pipe_escaped_cells) + " |"

    def tablehead(self, *header_cells: str, bold: bool = False) -> str:
        """Produces a Markdown table header from the given cells by joining each cell with pipes ("|") and wrapping the
        result in pipes, plus adding a header divider row. Cell contents have their pipes escaped with a backslash
        ("\\"). To bold the header cell contents, supply `bold = true`.

        Args:
            *header_cells (str): The header cells of the table header row.
            bold (bool, optional): Whether or not to bold the header's contents. Defaults to False.

        Returns:
            str: The Markdown table header row.
        """
        _pipe_escaped_cells = tuple(map(lambda cell: cell.replace("|", "\\|"), header_cells))
        if bold:
            _pipe_escaped_cells = tuple(MetadockHtmlNamespace().bold(cell) for cell in _pipe_escaped_cells)
        return self.tablerow(*_pipe_escaped_cells) + "\n" + self.tablerow(*(["---"] * len(_pipe_escaped_cells)))

    def convert_filter(self, md_content: str) -> str:
        """Filter which converts Markdown content to HTML, by invoking `marko.convert` (using github-flavored md).

        Args:
            md_content (str): The Markdown content to be converted to HTML.

        Returns:
            str: The HTML content.
        """
        return gfm.convert(md_content)

    def list_filter(self, values: str | Iterable[str]) -> str:
        """Filter which unpacks an iterable of values into a Markdown list, or formats a single value as a Markdown list
        element.

        Args:
            values (str | Iterable[str]): Piped input value(s) to be formatted as a Markdown list.

        Returns:
            str: The Markdown list.
        """
        if _is_nonstr_iter(values):
            return self.list(*values)
        return self.list(str(values))


class MetadockHtmlNamespace(MetadockNamespace):
    """Jinja namespace which owns HTML-related functions and filters.

    **Macros**:

        bold
        code
        details
        italic
        pre
        summary
        underline

    **Filters**:

        escape
        inline
    """

    exports = ["bold", "code", "details", "italic", "pre", "summary", "underline"]
    filters = ["escape", "inline"]

    def bold(self, content: str) -> str:
        """Wraps a string in HTML bold tags (<b></b>).

        Args:
            content (str): The content to be formatted as bold.

        Returns:
            str: The HTML bold content.
        """
        return f"<b>{content}</b>"

    def code(self, content: str) -> str:
        """Wraps a string in HTML code tags (<code></code>).

        Args:
            content (str): The content to be formatted as code.

        Returns:
            str: The HTML code content.
        """
        return f"<code>{content}</code>"

    def details(self, *contents: str) -> str:
        """Wraps a string in HTML details tags (<details></details>). Multiple arguments get separated by two line
        breaks.

        Args:
            *contents (str): The content to be wrapped in details tags. Multiple arguments get separated by two line
                breaks.

        Returns:
            str: The HTML details content.
        """
        indented_linesep_contents = "\n\n".join(contents).replace("\n", "\n")
        return f"<details>\n{indented_linesep_contents}\n</details>"

    def italic(self, content: str) -> str:
        """Wraps a string in HTML italic tags (<i></i>).

        Args:
            content (str): The content to be formatted as italic.

        Returns:
            str: The HTML italic content.
        """
        return f"<i>{content}</i>"

    def pre(self, content: str, indent: int = 0) -> str:
        """Wraps a string in preformatted HTML pre tags (<pre></pre>), and indents the content by the
        given amount.

        Args:
            content (str): The content to be formatted as pre-formatted code.
            indent (int, optional): Number of spaces which should be used to indent the contents. Defaults to 0.

        Returns:
            str: The HTML code block content.
        """
        indented_content = " " * indent + content.replace("\n", "\n" + " " * indent)
        return f"<pre>{indented_content}</pre>"

    def summary(self, content: str) -> str:
        """Wraps a string in HTML summary tags (<summary></summary>).

        Args:
            content (str): The content to be wrapped in summary tags.

        Returns:
            str: The HTML summary content.
        """
        return f"<summary>\n{content}\n</summary>"

    def underline(self, content: str) -> str:
        """Wraps a string in HTML underline tags (<u></u>).

        Args:
            content (str): The content to be formatted as underline.

        Returns:
            str: The HTML underline content.
        """
        return f"<u>{content}</u>"

    def escape_filter(self, content: str) -> str:
        """Filter which escapes a string by replacing all HTML special characters with their HTML entity equivalents.

        Args:
            content (str): Piped input string to be HTML-escaped.

        Returns:
            str: The escaped string.
        """
        return html.escape(content)

    def inline_filter(self, content: str) -> str:
        """Filter which inlines a string by replacing all newlines with HTML line-break <br> singleton tags.

        Args:
            content (str): Piped input string to be HTML-inlined.

        Returns:
            str: The HTML-inlined string.
        """
        return content.replace("\n", "<br>")


class MetadockEnv(MetadockNamespace):
    """Jinja namespace for the global Metadock environment, including all global macros, filters, and namespaces.

    **Macros**:

        debug

    **Namespaces**:

        html
        md

    **Filters**:

        chain
        inline
        with_prefix
        with_suffix
        zip
    """

    md = MetadockMdNamespace()
    html = MetadockHtmlNamespace()
    exports = ["debug"]
    namespaces = ["html", "md"]
    filters = ["chain", "inline", "with_prefix", "with_suffix", "zip"]

    def debug(self, message: str) -> Literal[""]:
        """Prints a debug message to stdout, and returns an empty string."""
        print(message)
        return ""

    def chain_filter(self, iterables: Sequence[Iterable[Any]]) -> Iterable[Any]:
        """Filter which flattens a sequence of iterables into a single iterable.

        Args:
            iterables (Sequence[Iterable[Any]]): Piped input sequence of iterables to be flattened.

        Returns:
            Iterable[Any]: The flattened iterable.
        """
        return itertools.chain.from_iterable(iterables)

    def inline_filter(self, value: str) -> str:
        """Filter which inlines a string by replacing all newlines with spaces, and all double spaces with single
        spaces.

        Args:
            value (str): Piped input string to be inlined.

        Returns:
            str: The inlined string.
        """
        return value.replace("\n", " ").replace("  ", " ")

    def with_prefix_filter(self, value: str, prefix: str, sep: str = "") -> str:
        """Filter which prepends a prefix to a string, with an optional separator.

        Args:
            value (str): Piped input string to be prefixed.
            prefix (str): Prefix to be concatenated to the beginning of the input string.
            sep (str, optional): Separator to place between prefix and string. Defaults to empty string.

        Returns:
            str: The prefixed string.
        """
        return sep.join((prefix, value))

    def with_suffix_filter(self, value: str, suffix: str, sep: str = "") -> str:
        """Filter which appends a suffix to a string, with an optional separator.

        Args:
            value (str): Piped input string to be suffixed.
            suffix (str): Suffix to be concatenated to the end of the input string.
            sep (str, optional): Separator to place between string and suffix. Defaults to empty string.

        Returns:
            str: The suffixed string.
        """
        return sep.join((value, suffix))

    def zip_filter(self, input_iterable: Iterable[Any], *iterables: Iterable[Any]) -> Iterable[tuple[Any, ...]]:
        """Filter which zips an input iterable with one or more iterables.

        Args:
            input_iterable (Iterable[Any]): Piped input iterable to be zipped (leftmost zipper).
            *iterables (Iterable[Any]): The iterables to be zipped with the input iterable.

        Returns:
            Iterable[tuple[Any, ...]]: The zipped iterables.
        """
        return zip(input_iterable, *iterables)
