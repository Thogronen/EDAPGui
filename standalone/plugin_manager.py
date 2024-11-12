import os
import sys
import importlib.util
import inspect
from plugin_interface import PluginInterface


class PluginManager:
    def __init__(self, parent, logger):
        self.parent = parent
        self.logger = logger
        self.plugins = {}
        self.plugin_paths = {}
        self._testing = False

    @property
    def testing(self):
        return self._testing

    def set_testing(self, value: bool):
        self._testing = value

    def log(self, message: str, level: str = 'INFO'):
        """Log messages appropriately based on testing mode."""
        if self.testing:
            getattr(self.logger, level.lower())(message)
        else:
            self.parent.debug_log(message, level=level)

    def load_plugin(self, plugin_path):
        self.log(f"Attempting to load plugin from: {plugin_path}", 'DEBUG')

        if not os.path.exists(plugin_path):
            self.log(f"Plugin path does not exist: {plugin_path}", 'ERROR')
            return False

        plugin_name = os.path.splitext(os.path.basename(plugin_path))[0]
        if plugin_name in self.plugins:
            self.log(f"Plugin '{plugin_name}' is already loaded", 'WARNING')
            return False

        try:
            # Add plugin directory and parent directory to path temporarily
            plugin_dir = os.path.dirname(os.path.abspath(plugin_path))
            parent_dir = os.path.dirname(plugin_dir)

            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)
                self.log(f"Added to sys.path: {plugin_dir}", 'DEBUG')

            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
                self.log(f"Added to sys.path: {parent_dir}", 'DEBUG')

            self.log(f"Current sys.path: {sys.path}", 'DEBUG')

            try:
                self.log(f"Creating spec for plugin: {plugin_path}", 'DEBUG')
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                if not spec or not spec.loader:
                    self.log(f"Could not create spec for plugin: {plugin_path}", 'ERROR')
                    return False

                self.log("Creating module from spec", 'DEBUG')
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                self.log(f"Module contents: {dir(module)}", 'DEBUG')

                # Check if PluginInterface is properly imported
                self.log(f"Checking if module has access to PluginInterface", 'DEBUG')
                plugin_interface = getattr(module, 'PluginInterface', None)
                if plugin_interface:
                    self.log("Module has PluginInterface", 'DEBUG')
                else:
                    self.log("Module does not have PluginInterface", 'ERROR')

                plugin_class = getattr(module, "Plugin", None)
                if not plugin_class:
                    self.log(f"No Plugin class found in {plugin_name}", 'ERROR')
                    return False

                self.log(f"Found Plugin class bases: {plugin_class.__bases__}", 'DEBUG')
                self.log(f"Plugin class MRO: {plugin_class.mro()}", 'DEBUG')

                if not issubclass(plugin_class, PluginInterface):
                    self.log(f"Plugin class is not a subclass of PluginInterface", 'ERROR')
                    self.log(f"Plugin class type: {type(plugin_class)}", 'DEBUG')
                    self.log(f"PluginInterface type: {type(PluginInterface)}", 'DEBUG')
                    self.log(f"Comparison: {plugin_class} vs {PluginInterface}", 'DEBUG')
                    return False

                self.log("Creating plugin instance", 'DEBUG')
                plugin = plugin_class(self.parent, self.logger)

                self.log("Calling plugin.load()", 'DEBUG')
                if not plugin.load():
                    self.log(f"Plugin {plugin_name} failed to load", 'ERROR')
                    return False

                self.plugins[plugin_name] = plugin
                self.plugin_paths[plugin_name] = plugin_path
                self.log(f"Successfully loaded plugin: {plugin_name}", 'INFO')
                return True

            finally:
                if plugin_dir in sys.path:
                    sys.path.remove(plugin_dir)
                    self.log(f"Removed from sys.path: {plugin_dir}", 'DEBUG')
                if parent_dir in sys.path:
                    sys.path.remove(parent_dir)
                    self.log(f"Removed from sys.path: {parent_dir}", 'DEBUG')

        except Exception as e:
            self.log(f"Error loading plugin {plugin_name}: {str(e)}", 'ERROR')
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}", 'ERROR')
            return False

    def unload_plugin(self, plugin_name):
        if plugin_name not in self.plugins:
            self.log(f"Plugin '{plugin_name}' is not loaded", 'WARNING')
            return False

        try:
            self.plugins[plugin_name].unload()
            del self.plugins[plugin_name]
            del self.plugin_paths[plugin_name]
            self.log(f"Successfully unloaded plugin: {plugin_name}", 'INFO')
            return True
        except Exception as e:
            self.log(f"Error unloading plugin {plugin_name}: {str(e)}", 'ERROR')
            return False

    def list_plugins(self):
        plugins_dir = os.path.join(os.getcwd(), "plugins")
        if not os.path.exists(plugins_dir):
            os.makedirs(plugins_dir)
            self.log(f"Created plugins directory at '{plugins_dir}'", 'INFO')

        plugin_files = [f for f in os.listdir(plugins_dir) if f.endswith('.py')]
        all_plugins = set(os.path.splitext(f)[0] for f in plugin_files)
        plugin_list = [(name, "Loaded" if name in self.plugins else "Not Loaded")
                       for name in all_plugins]

        if self.testing:
            print(f"Found plugins: {plugin_list}")

        return plugin_list