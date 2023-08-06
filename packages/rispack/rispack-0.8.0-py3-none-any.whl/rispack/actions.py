from rispack.stores import scoped_session


class BaseAction:
    @classmethod
    def run(cls, params):
        return cls()._scoped(params)

    @scoped_session
    def _scoped(self, params):
        return self.call(params)

    def call(self):
        raise NotImplementedError
