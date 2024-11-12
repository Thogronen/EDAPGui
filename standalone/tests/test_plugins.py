import os
import unittest
from unittest.mock import Mock
import sys

# Add parent directory to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from plugin_manager import PluginManager


class TestPluginSystem(unittest.TestCase):
    """Test the plugin system functionality including loading, unloading, and plugin lifecycle."""

    def setUp(self):
        """Set up test environment."""
        # Use the plugin directory from environment variable
        self.plugin_dir = os.environ.get('PLUGIN_DIR', 'plugins')
        print(f"\nPlugin directory path: {os.path.abspath(self.plugin_dir)}")

        # Path to test plugin
        self.test_plugin_path = os.path.join(self.plugin_dir, "test_plugin.py")

        # Ensure plugins directory exists
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            print(f"Created plugin directory: {self.plugin_dir}")

        if not os.path.exists(self.test_plugin_path):
            print(f"Warning: Test plugin not found at {self.test_plugin_path}")
            return False

        print(f"Using existing test plugin at: {self.test_plugin_path}")

        # Setup mocked environment with proper attributes
        self.logger = Mock()
        self.logger.messages = []  # Initialize messages list
        self.logger.debug = lambda msg: self.logger.messages.append(f"DEBUG: {msg}")
        self.logger.info = lambda msg: self.logger.messages.append(f"INFO: {msg}")
        self.logger.warning = lambda msg: self.logger.messages.append(f"WARNING: {msg}")
        self.logger.error = lambda msg: self.logger.messages.append(f"ERROR: {msg}")

        self.parent = Mock()
        self.plugin_manager = PluginManager(self.parent, self.logger)
        self.plugin_manager.set_testing(True)

    def test_plugin_lifecycle(self):
        """Test the complete lifecycle of a plugin including loading and unloading."""
        print("\nStarting plugin lifecycle test")
        print(f"Plugin file exists: {os.path.exists(self.test_plugin_path)}")

        with open(self.test_plugin_path, 'r') as f:
            print(f"Plugin content:\n{f.read()}")

        # Test loading
        try:
            result = self.plugin_manager.load_plugin(self.test_plugin_path)
            print(f"Plugin load result: {result}")
            if not result:
                print(f"Plugin manager state: {vars(self.plugin_manager)}")
                print("Recent log messages:")
                for msg in self.logger.messages:
                    print(f"  {msg}")
        except Exception as e:
            print(f"Exception during plugin load: {str(e)}")
            raise

        self.assertTrue(result, "Plugin should load successfully")
        self.assertIn("test_plugin", self.plugin_manager.plugins)

        # Test unloading
        result = self.plugin_manager.unload_plugin("test_plugin")
        self.assertTrue(result, "Plugin should unload successfully")
        self.assertNotIn("test_plugin", self.plugin_manager.plugins)


if __name__ == '__main__':
    unittest.main()