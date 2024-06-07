import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
from diceditor import DictionaryEditor


class DictionaryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Dictionary Manager")
        self.root.geometry("400x300")

        self.dictionaries = []
        self.load_dictionaries()

        self.create_widgets()

    def load_dictionaries(self):
        translations_folder = "translations"
        for filename in os.listdir(translations_folder):
            if filename.endswith(".json"):
                self.dictionaries.append(os.path.join(translations_folder, filename))

    def create_widgets(self):
        self.listbox = tk.Listbox(self.root, selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for dictionary in self.dictionaries:
            self.listbox.insert(tk.END, dictionary)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(btn_frame, text="Edit Dictionary", command=self.edit_dictionary).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="Add Dictionary", command=self.add_dictionary).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(
            btn_frame, text="Delete Dictionary", command=self.delete_dictionary
        ).pack(side=tk.LEFT, padx=5)

    def edit_dictionary(self):
        selected_index = self.listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "No dictionary selected")
            return
        dictionary_path = self.listbox.get(selected_index[0])
        self.open_editor(dictionary_path)

    def add_dictionary(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({"translations": {}}, f, ensure_ascii=False, indent=4)
            self.dictionaries.append(file_path)
            self.listbox.insert(tk.END, file_path)
            messagebox.showinfo("Success", "New dictionary created successfully")

    def delete_dictionary(self):
        selected_index = self.listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "No dictionary selected")
            return
        dictionary_path = self.listbox.get(selected_index[0])
        if messagebox.askyesno(
            "Delete", f"Are you sure you want to delete {dictionary_path}?"
        ):
            os.remove(dictionary_path)
            self.listbox.delete(selected_index)
            self.dictionaries.remove(dictionary_path)
            messagebox.showinfo("Success", "Dictionary deleted successfully")

    def open_editor(self, dictionary_path):
        editor_root = tk.Toplevel(self.root)
        DictionaryEditor(editor_root, dictionary_path)
        editor_root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = DictionaryManager(root)
    root.mainloop()
