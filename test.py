import customtkinter as ctk

import CTkFileDialog
from CTkFileDialog.Constants import PWD


def open_mini_file() -> None:
    file = CTkFileDialog.askopenfilename(
        style="Mini",
        autocomplete=True,
        initial_dir=PWD,
        title="Open File, please!",
        geometry=(
            "1320x720",  # Normal dialog geometry
            "500x400",  # Mini dialog geometry
        ),
    )
    if file:
        print(f"[+] Selected file -> {file}")
    else:
        print("[!] No file selected (Mini dialog cancelled)")


def open_normal_file() -> None:
    file = CTkFileDialog.askopenfilename(
        style="Default",
        autocomplete=True,
        tool_tip=True,
        initial_dir=PWD,  # Supports $HOME, %TMP%, etc.
        geometry=(
            "1320x720",  # Normal dialog geometry
            "500x400",  # Mini dialog geometry
        ),
        title="Open File, please!",
    )
    if file:
        print(f"[+] Selected file -> {file}")
    else:
        print("[!] No file selected (Default dialog cancelled)")


def main() -> None:
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("green")

    app = ctk.CTk()
    app.geometry("500x300")
    app.minsize(400, 250)
    app.title("File Selector")

    frame = ctk.CTkFrame(master=app, corner_radius=15)
    frame.pack(padx=40, pady=40, fill="both", expand=True)

    label = ctk.CTkLabel(master=frame, text="Select a file", font=("Arial", 18))
    label.pack(pady=(10, 20))

    ctk.CTkButton(
        master=frame,
        command=open_normal_file,
        text="📂 Full Dialog",
    ).pack(pady=10)

    ctk.CTkButton(
        master=frame,
        command=open_mini_file,
        text="🗂️ Mini Dialog",
    ).pack(pady=10)

    def toggle_theme() -> None:
        ctk.set_appearance_mode("Dark" if theme_switch.get() == 1 else "Light")

    theme_switch = ctk.CTkSwitch(master=frame, text="Theme Mode", command=toggle_theme)
    theme_switch.select()
    theme_switch.pack(pady=10, padx=10)

    app.mainloop()


if __name__ == "__main__":
    main()
