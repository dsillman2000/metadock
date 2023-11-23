class MetadockTableNamespace:
    exports = ["header", "row"]

    def row(self, *cells: str):
        return "| " + " | ".join(cells) + " |"

    def header(self, *header_cells: str, bold: bool = False):
        if bold:
            header_cells = tuple(f"<b>{cell}</b>" for cell in header_cells)
        return self.row(*header_cells) + "\n" + self.row(*(["---"] * len(header_cells)))


class MetadockEnv:
    table = MetadockTableNamespace()
    exports = ["blockquote", "codeblock", "debug", "list", "table"]

    def debug(self, message: str):
        print(message)
        return ""

    def blockquote(self, content: str):
        _blockquoted = content.rstrip().replace("\n", "\n> ")
        return f"> {_blockquoted}"

    def codeblock(self, content: str, language: str = ""):
        return f"```{language}\n{content.rstrip()}\n```"

    def list(self, *items: str):
        _list_prefixes = ("-", "*", "+")

        def _is_list(item: str):
            return item.startswith(_list_prefixes)

        indented_items = [item.replace("\n", "\n  ") for item in items]
        return "\n".join(
            (f"- {item}" if not _is_list(item) else f"  {indented_item}")
            for item, indented_item in zip(items, indented_items)
        )

    def dict(self):
        return {funcname: getattr(self, funcname) for funcname in self.exports}
