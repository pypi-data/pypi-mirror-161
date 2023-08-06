from inspector_commons.bridge.browser_bridge import BrowserBridge
from inspector_commons.config import Config
from inspector_commons.context import Context
from inspector_commons.utils import IS_WINDOWS


class BridgeConnector(BrowserBridge):
    def __init__(self, logger, *args, **kwargs):
        config = Config()
        config.set("remote", None)
        config.set("debug", True)
        context = Context(logger, config)
        super().__init__(context, *args, **kwargs)


if IS_WINDOWS:
    from inspector_commons.bridge.windows_bridge import WindowsBridge

    class WindowsBridgeConnector(WindowsBridge):
        def __init__(self, logger, *args, **kwargs):
            config = Config()
            config.set("remote", None)
            config.set("debug", True)
            context = Context(logger, config)
            super().__init__(context, *args, **kwargs)
