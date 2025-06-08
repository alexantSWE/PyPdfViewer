import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ... (the rest of the code is the same as the previous correct version) ...

class PDFViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced PDF Viewer")
        self.root.geometry("1000x800")
        # ... (rest of __init__ is unchanged) ...
        self.pdf_data = None
        self.filepath = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.dark_mode_enabled = tk.BooleanVar(value=False)
        self.photo_image = None
        self.canvas_image_item = None
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5, padx=5)
        self.setup_controls(control_frame)
        self.setup_display_area(main_frame)
        self.setup_key_bindings()

    # ... (setup_controls, setup_display_area, setup_key_bindings are unchanged) ...

    ### MODIFIED FUNCTION ###
    def open_pdf(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not filepath:
            # User cancelled the dialog, so we do nothing.
            return
        
        # --- Start of the robust reset logic ---
        # 1. A new file has been chosen. First, clear the canvas of any old image.
        if self.canvas_image_item:
            self.canvas.delete(self.canvas_image_item)
            self.canvas_image_item = None
            self.photo_image = None # Release the image reference
        
        # 2. Reset the data state before trying to load the new file.
        self.pdf_data = None

        try:
            # 3. Read the new file into memory.
            with open(filepath, "rb") as f:
                self.pdf_data = f.read()
            
            # 4. Open a temporary document to get page count.
            temp_doc = fitz.open(stream=self.pdf_data, filetype="pdf")
            self.total_pages = len(temp_doc)
            temp_doc.close()
            
            # 5. Reset state for the new file.
            self.filepath = filepath
            self.current_page = 0
            self.zoom_level = 1.0
            
            # 6. Render the first page. This will draw the new content.
            self.show_page()
            self.root.title(f"Enhanced PDF Viewer - {filepath.split('/')[-1]}")

        except Exception as e:
            # 7. If anything goes wrong, reset the entire UI to a clean, empty state.
            messagebox.showerror("Error", f"Failed to open PDF: {e}")
            self.pdf_data = None  # Ensure data is None
            self.update_ui()      # Update controls to show "Page 0 of 0", etc.
            self.root.title("Enhanced PDF Viewer") # Reset title


    # ... (show_page, toggle_dark_mode, update_ui, and all other methods are unchanged) ...
    def setup_controls(self, parent_frame):
        """Creates and places all the control widgets."""
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
        """Creates the canvas and scrollbars for displaying the PDF."""
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
        """Bind keyboard shortcuts."""
        self.root.bind("<Left>", lambda event: self.prev_page())
        self.root.bind("<Right>", lambda event: self.next_page())
        self.root.bind("<plus>", lambda event: self.zoom_in())
        self.root.bind("<minus>", lambda event: self.zoom_out())
        self.root.bind("<Control-o>", lambda event: self.open_pdf())
        
    def show_page(self):
        if not self.pdf_data: return

        if self.canvas_image_item:
            self.canvas.delete(self.canvas_image_item)

        doc = fitz.open(stream=self.pdf_data, filetype="pdf")
        page = doc.load_page(self.current_page)
        
        if self.dark_mode_enabled.get():
            page.invert_colors()

        mat = fitz.Matrix(self.zoom_level, self.zoom_level)
        pix = page.get_pixmap(matrix=mat)
        
        doc.close()
        
        img_data = pix.tobytes("ppm")
        self.photo_image = tk.PhotoImage(data=img_data)
        
        self.canvas_image_item = self.canvas.create_image(0, 0, anchor='nw', image=self.photo_image)
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        
        self.update_ui()
        
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