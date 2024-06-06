# gui.py
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import json
import logging
from translator import Translator
from dicmanager import DictionaryManager  # 导入词典管理器
from plugin_manager import PluginManager  # 导入插件管理器
from texteditor import TextEditor, open_editor  # 导入文本编辑器
import os

# 配置日志记录
logging.basicConfig(filename='translation.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Word Document Translator")
        self.root.geometry("600x400")

        self.language_var = tk.StringVar(value="en_cn")
        self.category_var = tk.StringVar(value="")
        self.input_file = None
        self.input_file_path = tk.StringVar(value="")
        self.strict_punctuation = tk.BooleanVar(value=True)
        self.ignore_case = tk.BooleanVar(value=False)
        self.partial_match = tk.BooleanVar(value=False)
        self.selected_category_path = tk.StringVar(value="")

        self.metadata = self.load_metadata()
        self.create_widgets()
        self.update_categories()
        logging.info('Translation app started')

    def load_metadata(self):
        try:
            with open('translations_metadata.json', 'r', encoding='utf-8') as f:
                logging.info('Loaded translations metadata')
                return json.load(f).get("translations", [])
        except FileNotFoundError:
            messagebox.showerror("Error", "translations_metadata.json not found")
            logging.error('translations_metadata.json not found')
            return []

    def update_categories(self, *args):
        selected_language = self.language_var.get()
        if not selected_language:
            self.category_var.set("")
            self.selected_category_path.set("")
            return
        
        categories = [item["description"] for item in self.metadata if item["file"].startswith(selected_language)]
        self.category_var.set("")
        menu = self.category_menu["menu"]
        menu.delete(0, "end")
        for category in categories:
            menu.add_command(label=category, command=lambda value=category: self.set_category(value))

    def set_category(self, category):
        self.category_var.set(category)
        category_file = next((item["file"] for item in self.metadata if item["description"] == category), None)
        if category_file:
            category_path = os.path.join('translations', category_file)
            self.selected_category_path.set(category_path)
            logging.info(f'Selected category file: {category_path}')

    def create_widgets(self):
        tk.Label(self.root, text="Language (e.g., en_cn):").grid(row=0, column=0, padx=10, pady=10)
        language_entry = tk.Entry(self.root, textvariable=self.language_var)
        language_entry.grid(row=0, column=1, padx=10, pady=10)
        language_entry.bind("<KeyRelease>", self.update_categories)

        tk.Label(self.root, text="Category:").grid(row=1, column=0, padx=10, pady=10)
        self.category_menu = tk.OptionMenu(self.root, self.category_var, "")
        self.category_menu.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Selected category path:").grid(row=2, column=0, padx=10, pady=10)
        tk.Label(self.root, textvariable=self.selected_category_path).grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Selected file:").grid(row=3, column=0, padx=10, pady=10)
        tk.Label(self.root, textvariable=self.input_file_path).grid(row=3, column=1, padx=10, pady=10)

        tk.Button(self.root, text="Load Word File", command=self.load_file).grid(row=4, column=0, padx=10, pady=10)
        tk.Button(self.root, text="Add Translation", command=self.add_translation).grid(row=4, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Strict punctuation:").grid(row=5, column=0, padx=10, pady=10)
        tk.Radiobutton(self.root, text="Yes", variable=self.strict_punctuation, value=True).grid(row=5, column=1, padx=10, pady=10)
        tk.Radiobutton(self.root, text="No", variable=self.strict_punctuation, value=False).grid(row=5, column=2, padx=10, pady=10)

        tk.Label(self.root, text="Ignore case:").grid(row=6, column=0, padx=10, pady=10)
        tk.Checkbutton(self.root, text="Yes", variable=self.ignore_case).grid(row=6, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Partial match:").grid(row=7, column=0, padx=10, pady=10)
        tk.Checkbutton(self.root, text="Yes", variable=self.partial_match).grid(row=7, column=1, padx=10, pady=10)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="determinate")
        self.progress.grid(row=8, column=0, columnspan=3, padx=10, pady=10)

        tk.Button(self.root, text="Translate Document", command=self.translate_document).grid(row=9, column=0, columnspan=3, padx=10, pady=10)
        tk.Button(self.root, text="Manage Dictionaries", command=self.open_dictionary_manager).grid(row=10, column=0, columnspan=3, padx=10, pady=10)  # 添加词库管理按钮
        tk.Button(self.root, text="Manage Plugins", command=self.open_plugin_manager).grid(row=11, column=0, columnspan=3, padx=10, pady=10)  # 添加插件管理按钮
        tk.Button(self.root, text="Edit Document", command=self.open_text_editor).grid(row=12, column=0, columnspan=3, padx=10, pady=10)  # 添加文档编辑按钮

    def load_file(self):
        self.input_file = filedialog.askopenfilename(filetypes=[("Word files", "*.docx")])
        if self.input_file:
            self.input_file_path.set(self.input_file)
            messagebox.showinfo("Info", f"Loaded file: {self.input_file}")
            logging.info(f'Loaded file: {self.input_file}')

    def add_translation(self):
        word = simpledialog.askstring("Input", "Enter the word or paragraph to translate:")
        translation = simpledialog.askstring("Input", "Enter the translation:")
        if word and translation:
            category_file = next((item["file"] for item in self.metadata if item["description"] == self.category_var.get()), None)
            if category_file:
                category_path = os.path.join('translations', category_file)
                translator = Translator(self.language_var.get(), category_path, self.strict_punctuation.get(), self.ignore_case.get(), self.partial_match.get())
                translator.add_translation(word, translation)
                messagebox.showinfo("Info", f"Added translation: {word} -> {translation}")
                logging.info(f'Added translation: {word} -> {translation}')

    def translate_document(self):
        if not self.input_file:
            messagebox.showerror("Error", "No Word file loaded")
            logging.error('No Word file loaded')
            return
        output_file = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word files", "*.docx")])
        if output_file:
            category_file = next((item["file"] for item in self.metadata if item["description"] == self.category_var.get()), None)
            if not category_file:
                messagebox.showerror("Error", "No category selected")
                logging.error('No category selected')
                return
            category_path = os.path.join('translations', category_file)
            translator = Translator(self.language_var.get(), category_path, self.strict_punctuation.get(), self.ignore_case.get(), self.partial_match.get())
            
            def update_progress(value):
                self.progress['value'] = value
                self.root.update_idletasks()
            
            untranslated_segments = translator.translate_document(self.input_file, output_file, update_progress)
            if untranslated_segments:
                result = messagebox.askyesno("Edit Translations", "Some segments were not translated. Would you like to edit them?")
                if result:
                    open_editor(untranslated_segments, output_file)
            else:
                messagebox.showinfo("Info", f"Translated document saved as: {output_file}")
                logging.info(f'Translated document saved as: {output_file}')
            self.progress['value'] = 0  # 重置进度条

    def open_dictionary_manager(self):
        manager_root = tk.Toplevel(self.root)
        DictionaryManager(manager_root)
        
    def open_plugin_manager(self):
        manager_root = tk.Toplevel(self.root)
        PluginManager(manager_root)
    
    def open_text_editor(self):
        editor_root = tk.Toplevel(self.root)
        TextEditor(editor_root, file_path=self.input_file)

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslationApp(root)
    root.mainloop()
