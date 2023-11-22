class MetadockEnv:
    exports = ["debug"]

    def debug(self, message: str):
        print(message)
        return ""

    def dict(self):
        return {funcname: getattr(self, funcname) for funcname in self.exports}
