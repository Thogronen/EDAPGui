class PluginInterface:
    """Base interface for all plugins."""
    def __init__(self, parent, logger):
        self.parent = parent
        self.logger = logger

    def load(self):
        """Load the plugin's functionalities."""
        raise NotImplementedError("Plugin must implement the load method")

    def unload(self):
        """Unload the plugin's functionalities."""
        raise NotImplementedError("Plugin must implement the unload method")