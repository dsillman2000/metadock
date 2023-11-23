class MetadockEnv:
    exports = ["debug", "table_row"]

    def debug(self, message: str):
        print(message)
        return ""

    def table_row(self, *cells: str):
        return "| " + " | ".join(cells) + " |"

    def dict(self):
        return {funcname: getattr(self, funcname) for funcname in self.exports}
