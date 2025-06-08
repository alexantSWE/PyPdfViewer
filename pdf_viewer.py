import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# --- Import Section ---
try:
    import fitz  # PyMuPDF
except ImportError:
    messagebox.showerror("Error", "PyMuPDF not installed. Run: pip install PyMuPDF")
    exit()

### NEW DEPENDENCY ###
try:
    from PIL import Image, ImageOps, ImageTk
except ImportError:
    messagebox.showerror("Error", "Pillow not installed. Run: pip install Pillow")
    exit()


class PDFViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced PDF Viewer")
        self.root.geometry("1000x800")

        # --- State Variables (Unchanged) ---
        self.pdf_data = None
        self.filepath = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.dark_mode_enabled = tk.BooleanVar(value=False)
        self.photo_image = None
        self.canvas_image_item = None

        # --- UI Layout (Unchanged) ---
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5, padx=5)
        self.setup_controls(control_frame)
        self.setup_display_area(main_frame)
        self.setup_key_bindings()

    ### MODIFIED FUNCTION: show_page ###
    def show_page(self):
        if not self.pdf_data: return

        if self.canvas_image_item:
            self.canvas.delete(self.canvas_image_item)

        # 1. Create a fresh document object from bytes
        doc = fitz.open(stream=self.pdf_data, filetype="pdf")
        page = doc.load_page(self.current_page)
        
        # 2. Get the normal pixmap (image data) from PyMuPDF
        mat = fitz.Matrix(self.zoom_level, self.zoom_level)
        pix = page.get_pixmap(matrix=mat, alpha=False) # No alpha channel needed
        
        doc.close()

        # 3. Create a Pillow Image from the raw pixmap data
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # 4. If dark mode is on, use Pillow to invert the image's colors
        if self.dark_mode_enabled.get():
            # Invert works on 'L' (grayscale) or 'RGB' images
            img = ImageOps.invert(img)

        # 5. Convert the (possibly inverted) Pillow Image to a Tkinter-compatible PhotoImage
        # This is the crucial bridge between Pillow and Tkinter
        self.photo_image = ImageTk.PhotoImage(image=img)
        
        # 6. Display the image on the canvas
        self.canvas_image_item = self.canvas.create_image(0, 0, anchor='nw', image=self.photo_image)
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        
        self.update_ui()

    # --- All other methods are unchanged and correct ---
    
    def setup_controls(self, parent_frame):
        ttk.Button(parent_frame, text="Open PDF", command=self.open_pdf).pack(side=tk.LEFT, padx=2)
        self.prev_button = ttk.Button(parent_frame, text="<", command=self.prev_page, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=2)
        self.page_entry = ttk.Entry(parent_frame, width=4)
        self.page_entry.pack(side=tk.LEFT, padx=2)
        self.page_entry.bind("<Return>", self.go_to_page)
        self.page_label = ttk.Label(parent_frame, text="/ 0")
        self.page_label.pack(side=tk.LEFT, padx=2)
        self.next_button = ttk.Button(parent_frame, text=">", command=self.next_page, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=(2, 10))
        ttk.Button(parent_frame, text="-", command=self.zoom_out, width=2).pack(side=tk.LEFT, padx=2)
        self.zoom_label = ttk.Label(parent_frame, text="100%")
        self.zoom_label.pack(side=tk.LEFT, padx=2)
        ttk.Button(parent_frame, text="+", command=self.zoom_in, width=2).pack(side=tk.LEFT, padx=2)
        ttk.Separator(parent_frame, orient='vertical').pack(side=tk.LEFT, padx=(10, 5), fill='y')
        dark_mode_check = ttk.Checkbutton(
            parent_frame, text="Dark Mode", variable=self.dark_mode_enabled, command=self.toggle_dark_mode
        )
        dark_mode_check.pack(side=tk.LEFT, padx=5)

    def setup_display_area(self, parent_frame):
        display_frame = ttk.Frame(parent_frame, relief="sunken")
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        self.canvas = tk.Canvas(display_frame, bg="gray")
        v_scroll = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_columnconfigure(0, weight=1)

    def setup_key_bindings(self):
        self.root.bind("<Left>", lambda event: self.prev_page())
        self.root.bind("<Right>", lambda event: self.next_page())
        self.root.bind("<plus>", lambda event: self.zoom_in())
        self.root.bind("<minus>", lambda event: self.zoom_out())
        self.root.bind("<Control-o>", lambda event: self.open_pdf())

    def open_pdf(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not filepath: return
        if self.canvas_image_item:
            self.canvas.delete(self.canvas_image_item)
            self.canvas_image_item = None
            self.photo_image = None
        self.pdf_data = None
        try:
            with open(filepath, "rb") as f:
                self.pdf_data = f.read()
            temp_doc = fitz.open(stream=self.pdf_data, filetype="pdf")
            self.total_pages = len(temp_doc)
            temp_doc.close()
            self.filepath = filepath
            self.current_page = 0
            self.zoom_level = 1.0
            self.show_page()
            self.root.title(f"Enhanced PDF Viewer - {filepath.split('/')[-1]}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF: {e}")
            self.pdf_data = None
            self.update_ui()
            self.root.title("Enhanced PDF Viewer")
        
    def toggle_dark_mode(self):
        bg_color = "#333333" if self.dark_mode_enabled.get() else "gray"
        self.canvas.config(bg=bg_color)
        if self.pdf_data:
            self.show_page()

    def update_ui(self):
        if not self.pdf_data:
            self.page_label.config(text="/ 0")
            self.page_entry.delete(0, tk.END)
            self.zoom_label.config(text="---%")
            self.prev_button['state'] = tk.DISABLED
            self.next_button['state'] = tk.DISABLED
            return
        self.page_label.config(text=f"/ {self.total_pages}")
        self.page_entry.delete(0, tk.END)
        self.page_entry.insert(0, str(self.current_page + 1))
        self.prev_button['state'] = tk.NORMAL if self.current_page > 0 else tk.DISABLED
        self.next_button['state'] = tk.NORMAL if self.current_page < self.total_pages - 1 else tk.DISABLED
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")

    def next_page(self):
        if self.pdf_data and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.show_page()

    def prev_page(self):
        if self.pdf_data and self.current_page > 0:
            self.current_page -= 1
            self.show_page()

    def go_to_page(self, event=None):
        if not self.pdf_data: return
        try:
            page_num = int(self.page_entry.get())
            if 1 <= page_num <= self.total_pages:
                self.current_page = page_num - 1
                self.show_page()
            else:
                messagebox.showwarning("Warning", f"Page number must be between 1 and {self.total_pages}.")
                self.update_ui()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid page number.")
            self.update_ui()

    def zoom_in(self):
        if not self.pdf_data: return
        self.zoom_level *= 1.2
        self.show_page()

    def zoom_out(self):
        if not self.pdf_data: return
        if self.zoom_level / 1.2 > 0.1:
            self.zoom_level /= 1.2
            self.show_page()


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFViewer(root)
    root.mainloop()