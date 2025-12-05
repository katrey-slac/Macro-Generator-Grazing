import tkinter as tk
from pathlib import Path


def show_success_popup(root, directory, macro_name):
    """
    Display a popup window indicating the macro file was successfully saved.
    Includes a copyable command for SPEC.
    """
    popup = tk.Toplevel(root)
    popup.title("Success")
    popup.geometry("500x175")
    popup.resizable(False, False)

    # Message Label
    tk.Label(popup, text="File saved successfully!\nRun this in SPEC:", font=("Arial", 10)).pack(pady=(10, 5))

    path = Path(directory)
    print(path)
    new_path = Path(*path.parts[2:]).as_posix()

    # Copyable Text
    cmd_text = f"qdo ./{new_path}/{macro_name}.txt"

    # Frame for Text and Scrollbar
    text_frame = tk.Frame(popup)
    text_frame.pack(pady=(0, 10))

    x_scroll = tk.Scrollbar(text_frame, orient="horizontal")
    x_scroll.pack(side="bottom", fill="x")

    text_box = tk.Text(
        text_frame, height=1, width=60, font=("Courier", 10),
        wrap="none", xscrollcommand=x_scroll.set
    )
    text_box.insert(tk.END, cmd_text)
    text_box.configure(state="disabled")
    text_box.pack()
    x_scroll.config(command=text_box.xview)

    # Copy button
    def copy_to_clipboard():
        root.clipboard_clear()
        root.clipboard_append(cmd_text)

    tk.Button(popup, text="Copy to Clipboard", command=copy_to_clipboard,
              bg="PaleTurquoise1", fg="black").pack()

    # Close button
    tk.Button(popup, text="Close", command=popup.destroy, bg="red3", fg="white").pack(pady=5)