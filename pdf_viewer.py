import tkinter as tk
from tkinter import ttk, filedialog
import fitz  # PyMuPDF

class PDFViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple PDF Viewer")
        self.root.geometry("800x600")

        # --- State Variables ---
        self.pdf_document = None
        self.current_page = 0
        self.total_pages = 0
        # This is crucial to prevent the image from being garbage-collected
        self.photo_image = None 

        # --- UI Elements ---
        # Frame for controls
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=5)

        # Buttons and Label
        self.open_button = ttk.Button(control_frame, text="Open PDF", command=self.open_pdf)
        self.open_button.pack(side=tk.LEFT, padx=5)

        self.prev_button = ttk.Button(control_frame, text="< Previous", command=self.prev_page, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.page_label = ttk.Label(control_frame, text="Page 0 of 0")
        self.page_label.pack(side=tk.LEFT, padx=5)

        self.next_button = ttk.Button(control_frame, text="Next >", command=self.next_page, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5)

        # Main display area for the PDF page
        self.pdf_label = ttk.Label(self.root)
        self.pdf_label.pack(expand=True, fill=tk.BOTH)

    def open_pdf(self):
        filepath = filedialog.askopenfilename(
            title="Open a PDF file",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not filepath:
            return

        try:
            self.pdf_document = fitz.open(filepath)
            self.total_pages = len(self.pdf_document)
            self.current_page = 0
            self.show_page()
        except Exception as e:
            # Handle potential errors like corrupted files
            tk.messagebox.showerror("Error", f"Failed to open PDF: {e}")


    def show_page(self):
        if not self.pdf_document:
            return

        # Load the page
        page = self.pdf_document.load_page(self.current_page)
        
        # Render the page to a pixmap (an image)
        # The zoom factor can be adjusted for higher/lower resolution
        zoom = 1.5  # Increase for better quality
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        # Convert the pixmap to a format Tkinter can use
        # The 'ppm' format is a simple, uncompressed format that Tkinter's PhotoImage understands
        img_data = pix.tobytes("ppm")
        self.photo_image = tk.PhotoImage(data=img_data)
        
        # Update the label with the new image
        self.pdf_label.config(image=self.photo_image)
        
        # Update the page number label and button states
        self.update_ui()

    def update_ui(self):
        """Updates the page number label and button states."""
        self.page_label.config(text=f"Page {self.current_page + 1} of {self.total_pages}")
        
        # Enable/disable navigation buttons
        self.prev_button['state'] = tk.NORMAL if self.current_page > 0 else tk.DISABLED
        self.next_button['state'] = tk.NORMAL if self.current_page < self.total_pages - 1 else tk.DISABLED

    def next_page(self):
        if self.pdf_document and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.show_page()

    def prev_page(self):
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.show_page()

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFViewer(root)
    root.mainloop()