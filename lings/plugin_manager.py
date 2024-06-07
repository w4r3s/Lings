# plugin_manager.py

import tkinter as tk
from tkinter import ttk, messagebox
import json
import importlib
import os
import logging

class PluginManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Plugin Manager")
        self.plugins = self.load_plugins()
        self.create_widgets()

    def load_plugins(self):
        with open("plugins/plugin_config.json", "r") as file:
            config = json.load(file)
        plugins = config["plugins"]
        for plugin in plugins:
            plugin["module"] = importlib.import_module(plugin["module"])
        return plugins

    def create_widgets(self):
        self.tree = ttk.Treeview(self.root, columns=("Name", "Status"), show="headings")
        self.tree.heading("Name", text="Plugin Name")
        self.tree.heading("Status", text="Status")
        self.tree.pack(fill=tk.BOTH, expand=True)

        for plugin in self.plugins:
            status = "Enabled" if plugin["enabled"] else "Disabled"
            self.tree.insert("", "end", values=(plugin["name"], status))

        self.tree.bind("<Double-1>", self.toggle_plugin)

    def toggle_plugin(self, event):
        selected_item = self.tree.selection()[0]
        plugin_name = self.tree.item(selected_item, "values")[0]
        for plugin in self.plugins:
            if plugin["name"] == plugin_name:
                if plugin["enabled"]:
                    plugin["module"].deactivate()
                    plugin["enabled"] = False
                    self.tree.item(selected_item, values=(plugin_name, "Disabled"))
                    logging.info(f'Disabled plugin {plugin_name}')
                else:
                    plugin["module"].activate()
                    plugin["enabled"] = True
                    self.tree.item(selected_item, values=(plugin_name, "Enabled"))
                    logging.info(f'Enabled plugin {plugin_name}')
                self.save_plugins()
                break

    def save_plugins(self):
        config = {"plugins": []}
        for plugin in self.plugins:
            config["plugins"].append({
                "name": plugin["name"],
                "module": plugin["module"].__name__,
                "enabled": plugin["enabled"]
            })
        with open("data/plugin_config.json", "w") as file:
            json.dump(config, file, indent=4)

def open_plugin_manager():
    root = tk.Toplevel()
    PluginManager(root)
    root.mainloop()
