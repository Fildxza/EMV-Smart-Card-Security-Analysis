import traceback
import tkinter as tk
from tkinter import messagebox

from dashboard import main


def run_with_error_dialog() -> None:
    try:
        main()
    except Exception:
        error_text = traceback.format_exc()
        print(error_text)

        with open("startup_error.log", "w", encoding="utf-8") as log_file:
            log_file.write(error_text)

        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "EMV Dashboard Startup Error",
                "Application failed to start.\n\n"
                "Error details have been saved to startup_error.log\n\n"
                f"{error_text}",
            )
            root.destroy()
        except Exception:
            pass

        raise


if __name__ == "__main__":
    run_with_error_dialog()
