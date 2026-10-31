"""Generate and save a QR code for a website URL.

Install dependencies: python -m pip install -r requirements.txt
Run the application: python qr_generator.py
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from urllib.parse import urlsplit

import qrcode
from PIL import Image, ImageTk
from qrcode.exceptions import DataOverflowError


def create_qr_image(url):
    """Validate an HTTP(S) URL and return its QR code as a Pillow image."""
    url = url.strip()
    if not url or any(character.isspace() for character in url):
        raise ValueError("Enter a URL without spaces.")

    parts = urlsplit(url)
    if parts.scheme.lower() not in ("http", "https") or not parts.hostname:
        raise ValueError("Enter a complete URL, such as https://www.bioxsystems.com/.")
    # Accessing port also checks for malformed or out-of-range port numbers.
    _ = parts.port

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


class QRGenerator:
    """A small desktop interface for creating QR codes."""

    def __init__(self, root):
        self.root = root
        self.qr_image = None
        self.preview_image = None
        root.title("URL QR Code Generator")
        root.resizable(False, False)

        frame = ttk.Frame(root, padding=20)
        frame.pack()
        ttk.Label(frame, text="QR Code Generator", font=("Arial", 20, "bold")).pack(pady=8)
        ttk.Label(frame, text="Enter a website URL including http:// or https://").pack()

        self.url = tk.StringVar(value="https://www.bioxsystems.com/")
        entry = ttk.Entry(frame, textvariable=self.url, width=58)
        entry.pack(pady=10)
        entry.bind("<Return>", lambda event: self.generate())
        ttk.Button(frame, text="Generate QR Code", command=self.generate).pack()

        self.preview = ttk.Label(frame, text="Your QR code will appear here.", anchor="center")
        self.preview.pack(pady=20)
        self.save_button = ttk.Button(frame, text="Save PNG", command=self.save, state="disabled")
        self.save_button.pack()
        self.status = tk.StringVar(value="Ready")
        ttk.Label(frame, textvariable=self.status).pack(pady=10)
        entry.focus_set()

    def generate(self):
        """Create a QR image and show a preview without contacting the website."""
        try:
            new_image = create_qr_image(self.url.get())
        except (ValueError, DataOverflowError) as error:
            messagebox.showerror("Cannot generate QR code", str(error) or "URL is too long.")
            return

        self.qr_image = new_image
        # Resize only the preview; save the original for a crisp, scannable PNG.
        preview = new_image.copy()
        preview.thumbnail((360, 360), Image.Resampling.NEAREST)
        self.preview_image = ImageTk.PhotoImage(preview)
        self.preview.configure(image=self.preview_image, text="")
        self.save_button.configure(state="normal")
        self.status.set("QR code generated. Scan it or save the PNG.")

    def save(self):
        """Let the user choose where to save the generated QR image."""
        if self.qr_image is None:
            return
        path = filedialog.asksaveasfilename(
            title="Save QR Code",
            defaultextension=".png",
            initialfile="qr_code.png",
            filetypes=[("PNG image", "*.png")],
        )
        if not path:
            return
        try:
            self.qr_image.save(path, format="PNG")
        except OSError as error:
            messagebox.showerror("Cannot save image", str(error))
            return
        self.status.set("QR code saved successfully.")


def main():
    """Start the application only when this file is run directly."""
    root = tk.Tk()
    QRGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
