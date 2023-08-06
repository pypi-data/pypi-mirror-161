from inspector_commons.bridge.base import Bridge, traceback


class DatabaseMixin(Bridge):
    @traceback
    def names(self):
        return self.ctx.database.names

    @traceback
    def load(self):
        try:
            super().load()
        except AttributeError:
            pass

        name = self.ctx.selected
        if name is None:
            return []

        locator = self.ctx.load_locator(name)
        if locator is None:
            self.logger.error("No locator with name: %s", name)
            return []

        return name, locator

    @traceback
    def save(self, name, locator):
        try:
            super().save()
        except AttributeError:
            pass

        self.ctx.database.update(name, locator)
        self.ctx.force_update()
