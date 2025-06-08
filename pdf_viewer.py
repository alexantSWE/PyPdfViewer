import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import fitz  # PyMuPDF
except ImportError:
    messagebox.showerror(
        "Error", 
        "PyMuPDF is not installed. Please install it using: pip install PyMuPDF"
    )
    exit()

class PDFViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced PDF Viewer")
        self.root.geometry("1000x800")

        # --- State Variables ---
        self.pdf_document = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0  # Initial zoom level
        
        # This is crucial to prevent the image from being garbage-collected
        self.photo_image = None
        # This will hold the ID of the image on the canvas
        self.canvas_image_item = None

        # --- UI Layout ---
        # Main frame to hold all widgets
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame for controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5, padx=5)

        # --- Control Widgets ---
        self.setup_controls(control_frame)
        
        # --- Display Area (Canvas with Scrollbars) ---
        self.setup_display_area(main_frame)
        
        # --- Keyboard Bindings ---
        self.setup_key_bindings()

    def setup_controls(self, parent_frame):
        """Creates and places all the control widgets."""
        ttk.Button(parent_frame, text="Open PDF", command=self.open_pdf).pack(side=tk.LEFT, padx=2)
        
        # Navigation
        self.prev_button = ttk.Button(parent_frame, text="<", command=self.prev_page, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=2)

        self.page_entry = ttk.Entry(parent_frame, width=4)
        self.page_entry.pack(side=tk.LEFT, padx=2)
        self.page_entry.bind("<Return>", self.go_to_page)
        
        self.page_label = ttk.Label(parent_frame, text="/ 0")
        self.page_label.pack(side=tk.LEFT, padx=2)

        self.next_button = ttk.Button(parent_frame, text=">", command=self.next_page, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=(2, 10))

        # Zoom
        ttk.Button(parent_frame, text="-", command=self.zoom_out, width=2).pack(side=tk.LEFT, padx=2)
        self.zoom_label = ttk.Label(parent_frame, text="100%")
        self.zoom_label.pack(side=tk.LEFT, padx=2)
        ttk.Button(parent_frame, text="+", command=self.zoom_in, width=2).pack(side=tk.LEFT, padx=2)

    def setup_display_area(self, parent_frame):
        """Creates the canvas and scrollbars for displaying the PDF."""
        display_frame = ttk.Frame(parent_frame, relief="sunken")
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        self.canvas = tk.Canvas(display_frame, bg="gray")
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid layout for canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        # Make the canvas expandable
        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_columnconfigure(0, weight=1)

    def setup_key_bindings(self):
        """Bind keyboard shortcuts."""
        self.root.bind("<Left>", lambda event: self.prev_page())
        self.root.bind("<Right>", lambda event: self.next_page())
        self.root.bind("<plus>", lambda event: self.zoom_in())
        self.root.bind("<minus>", lambda event: self.zoom_out())

    def open_pdf(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not filepath:
            return

        try:
            # Close previous document if open
            if self.pdf_document:
                self.pdf_document.close()
                
            self.pdf_document = fitz.open(filepath)
            self.total_pages = len(self.pdf_document)
            self.current_page = 0
            self.zoom_level = 1.0  # Reset zoom on new file
            self.show_page()
            self.root.title(f"Enhanced PDF Viewer - {filepath.split('/')[-1]}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF: {e}")
            self.pdf_document = None # Reset state on failure

    def show_page(self):
        if not self.pdf_document:
            return

        # Clear the canvas before drawing the new page
        if self.canvas_image_item:
            self.canvas.delete(self.canvas_image_item)

        page = self.pdf_document.load_page(self.current_page)
        
        # Render page with current zoom level
        mat = fitz.Matrix(self.zoom_level, self.zoom_level)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert pixmap to a PhotoImage
        img_data = pix.tobytes("ppm")
        self.photo_image = tk.PhotoImage(data=img_data)
        
        # Display the image on the canvas
        self.canvas_image_item = self.canvas.create_image(0, 0, anchor='nw', image=self.photo_image)
        
        # Update the canvas scroll region to match the image size
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        
        self.update_ui()

    def update_ui(self):
        """Updates all UI elements based on the current state."""
        if not self.pdf_document:
            self.page_label.config(text="/ 0")
            self.page_entry.delete(0, tk.END)
            self.zoom_label.config(text="---%")
            return

        # Update page navigation
        self.page_label.config(text=f"/ {self.total_pages}")
        self.page_entry.delete(0, tk.END)
        self.page_entry.insert(0, str(self.current_page + 1))
        
        self.prev_button['state'] = tk.NORMAL if self.current_page > 0 else tk.DISABLED
        self.next_button['state'] = tk.NORMAL if self.current_page < self.total_pages - 1 else tk.DISABLED

        # Update zoom label
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")

    def next_page(self):
        if self.pdf_document and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.show_page()

    def prev_page(self):
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.show_page()

    def go_to_page(self, event=None):
        if not self.pdf_document:
            return
        try:
            page_num = int(self.page_entry.get())
            if 1 <= page_num <= self.total_pages:
                self.current_page = page_num - 1
                self.show_page()
            else:
                messagebox.showwarning("Warning", f"Page number must be between 1 and {self.total_pages}.")
                self.update_ui() # Reset entry to current page
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid page number.")
            self.update_ui() # Reset entry to current page

    def zoom_in(self):
        if not self.pdf_document: return
        self.zoom_level *= 1.2
        self.show_page()

    def zoom_out(self):
        if not self.pdf_document: return
        if self.zoom_level / 1.2 > 0.1: # Prevent zooming too small
            self.zoom_level /= 1.2
            self.show_page()

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFViewer(root)
    root.mainloop()