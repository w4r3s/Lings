# diceditor.py
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import json
import pandas as pd


class DictionaryEditor:
    def __init__(self, root, file_path):
        self.root = root
        self.root.title("Dictionary Editor")

        self.file_path = file_path
        self.data = pd.DataFrame(columns=["Original", "Translation"])
        self.font_size = tk.IntVar(value=10)

        self.create_widgets()
        self.load_dictionary()

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Dictionary File:").grid(row=0, column=0, sticky="w")
        tk.Entry(
            frame,
            textvariable=tk.StringVar(value=self.file_path),
            state="readonly",
            width=50,
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tree_frame = tk.Frame(frame)
        tree_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Original", "Translation"),
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("Original", text="Original")
        self.tree.heading("Translation", text="Translation")
        self.tree.column("Original", anchor="w", width=300)
        self.tree.column("Translation", anchor="w", width=300)

        self.vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(
            tree_frame, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(yscroll=self.vsb.set, xscroll=self.hsb.set)

        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        self.update_treeview_style()

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Return>", self.on_return_key)
        self.tree.bind("<Escape>", self.on_escape_key)

        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        button_frame = tk.Frame(self.root)
        button_frame.pack(padx=10, pady=5, fill=tk.X)

        tk.Button(button_frame, text="Add Entry", command=self.add_entry).grid(
            row=0, column=0, padx=5, pady=5
        )
        tk.Button(button_frame, text="Delete Entry", command=self.delete_entry).grid(
            row=0, column=1, padx=5, pady=5
        )
        tk.Button(button_frame, text="Save", command=self.save_dictionary).grid(
            row=0, column=2, padx=5, pady=5
        )

        tk.Label(button_frame, text="Font Size:").grid(row=1, column=0, padx=5, pady=5)
        tk.Spinbox(
            button_frame,
            from_=8,
            to=20,
            textvariable=self.font_size,
            command=self.update_treeview_style,
        ).grid(row=1, column=1, padx=5, pady=5)

    def load_dictionary(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f).get("translations", {})
            self.data = pd.DataFrame(
                list(data.items()), columns=["Original", "Translation"]
            )
        self.update_treeview()

    def update_treeview(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, (_, row) in enumerate(self.data.iterrows()):
            tags = ("evenrow",) if i % 2 == 0 else ("oddrow",)
            self.tree.insert(
                "",
                "end",
                iid=i,
                values=(row["Original"], row["Translation"]),
                tags=tags,
            )

    def update_treeview_style(self):
        font_size = self.font_size.get()
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", font_size), rowheight=font_size + 10)
        style.configure("Treeview.Heading", font=("Arial", font_size, "bold"))
        style.map(
            "Treeview",
            background=[("selected", "gray90")],
            foreground=[("selected", "black")],
        )
        self.tree.tag_configure("oddrow", background="white")
        self.tree.tag_configure("evenrow", background="lightblue")

    def add_entry(self):
        original = simpledialog.askstring("Add Entry", "Enter the original text:")
        translation = simpledialog.askstring("Add Entry", "Enter the translation:")
        if original and translation:
            new_row = pd.DataFrame(
                {"Original": [original], "Translation": [translation]}
            )
            self.data = pd.concat([self.data, new_row], ignore_index=True)
            self.update_treeview()

    def delete_entry(self):
        selected_item = self.tree.selection()
        if selected_item:
            original = self.tree.item(selected_item, "values")[0]
            self.data = self.data[self.data["Original"] != original]
            self.update_treeview()

    def save_dictionary(self):
        data_dict = {
            row["Original"]: row["Translation"] for _, row in self.data.iterrows()
        }
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump({"translations": data_dict}, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Save Dictionary", "Dictionary saved successfully.")

    def on_double_click(self, event):
        if not self.tree.selection():
            return
        self.editing_item = self.tree.selection()[0]
        self.editing_column = self.tree.identify_column(event.x)
        self.start_edit()

    def on_return_key(self, event):
        self.save_edit()

    def on_escape_key(self, event):
        self.cancel_edit()

    def start_edit(self):
        if not self.editing_column:
            return
        item = self.tree.item(self.editing_item, "values")
        column = int(self.editing_column[1:]) - 1  # column name to index
        if column < 0:
            return
        x, y, width, height = self.tree.bbox(self.editing_item, self.editing_column)
        self.entry_edit = tk.Entry(self.tree, width=width // 10)
        self.entry_edit.insert(0, item[column])
        self.entry_edit.select_range(0, tk.END)
        self.entry_edit.place(x=x, y=y, width=width, height=height)
        self.entry_edit.focus_set()

    def save_edit(self):
        new_value = self.entry_edit.get()
        column = int(self.editing_column[1:]) - 1
        self.tree.set(self.editing_item, column=column, value=new_value)
        original = self.tree.item(self.editing_item, "values")[0]
        self.data.loc[
            self.data["Original"] == original, self.tree["columns"][column]
        ] = new_value
        self.entry_edit.destroy()
        self.update_treeview()

    def cancel_edit(self):
        self.entry_edit.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = DictionaryEditor(root, "translations/en_cn_passport.json")
    root.mainloop()
