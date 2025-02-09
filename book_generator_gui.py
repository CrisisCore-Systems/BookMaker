#!/usr/bin/env python3
"""
Low-Content Book Generator (GUI with Templates) for Amazon KDP
---------------------------------------------------------------

This script presents a graphical user interface with a list of predetermined templates 
(e.g., Daily Journal, Notebook, Planner, Dotted Journal) so you can quickly pre‑populate 
fields for a typical low‑content book. You may modify any field if desired and click “Generate PDF.”
The PDF is built using ReportLab and is ready for upload to Amazon KDP.

Dependencies:
  - Python 3.x
  - ReportLab (install with: pip install reportlab)
  - Tkinter (usually included with Python)
  
Usage:
  Simply run this script (double‑click or “python book_generator_gui.py”), choose a template 
  (or “Custom”), adjust settings if desired, and click “Generate PDF.”
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------------------
# PDF Generation Functions
# ---------------------------

def inches_to_points(inches):
    """Convert inches to PDF points (1 inch = 72 points)."""
    return inches * inch

def generate_cover_page(c, title, subtitle, author, width_pt, height_pt, cover_image=None, custom_font=None):
    """
    Generate the cover page.
    If a valid cover_image path is provided, the image is used as the background.
    Then the title, subtitle, and author are drawn (centered).
    """
    if cover_image and os.path.exists(cover_image):
        try:
            c.drawImage(cover_image, 0, 0, width=width_pt, height=height_pt,
                        preserveAspectRatio=True, mask='auto')
        except Exception as e:
            messagebox.showwarning("Cover Image Warning", f"Could not load cover image: {e}")
            c.setFillColorRGB(1, 1, 1)
            c.rect(0, 0, width_pt, height_pt, fill=1)
    else:
        c.setFillColorRGB(1, 1, 1)
        c.rect(0, 0, width_pt, height_pt, fill=1)

    # Text properties
    title_font_size = 36
    subtitle_font_size = 24
    author_font_size = 18

    y_position = height_pt - inches_to_points(1.5)
    if custom_font:
        c.setFont(custom_font, title_font_size)
    else:
        c.setFont("Helvetica-Bold", title_font_size)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(width_pt / 2, y_position, title)

    if subtitle:
        y_position -= title_font_size + 10
        if custom_font:
            c.setFont(custom_font, subtitle_font_size)
        else:
            c.setFont("Helvetica", subtitle_font_size)
        c.drawCentredString(width_pt / 2, y_position, subtitle)

    if author:
        y_position -= subtitle_font_size + 10
        if custom_font:
            c.setFont(custom_font, author_font_size)
        else:
            c.setFont("Helvetica-Oblique", author_font_size)
        c.drawCentredString(width_pt / 2, y_position, f"By {author}")

    c.showPage()

def generate_interior_page(c, page_type, width_pt, height_pt, margins, line_spacing, dot_spacing,
                           page_number=None, add_page_numbers=False, watermark="", header_text="",
                           footer_text="", custom_font=None, grid_spacing=None):
    """
    Generate one interior page according to the chosen design.
    Draws lines, dots, grid (or blank) within the defined margins and overlays
    optional watermark, header, footer, and page number.
    """
    left = inches_to_points(margins['left'])
    right = width_pt - inches_to_points(margins['right'])
    top = height_pt - inches_to_points(margins['top'])
    bottom = inches_to_points(margins['bottom'])

    if page_type == 'lined':
        spacing_pt = inches_to_points(line_spacing)
        c.setLineWidth(0.5)
        y = top - spacing_pt
        while y > bottom:
            c.line(left, y, right, y)
            y -= spacing_pt
    elif page_type == 'dotted':
        spacing_pt = inches_to_points(dot_spacing)
        dot_radius = 1
        c.setFillColorRGB(0.5, 0.5, 0.5)
        y = bottom + spacing_pt / 2
        while y < top:
            x = left + spacing_pt / 2
            while x < right:
                c.circle(x, y, dot_radius, fill=1, stroke=0)
                x += spacing_pt
            y += spacing_pt
    elif page_type == 'grid':
        spacing = inches_to_points(grid_spacing if grid_spacing is not None else line_spacing)
        c.setLineWidth(0.5)
        y = top - spacing
        while y > bottom:
            c.line(left, y, right, y)
            y -= spacing
        x = left + spacing
        while x < right:
            c.line(x, top, x, bottom)
            x += spacing
    elif page_type == 'blank':
        pass  # No interior design
    else:
        raise ValueError(f"Unsupported page type: {page_type}")

    # Watermark (diagonally centered)
    if watermark:
        c.saveState()
        try:
            c.setFillAlpha(0.1)
        except Exception:
            pass
        if custom_font:
            c.setFont(custom_font, 50)
        else:
            c.setFont("Helvetica", 50)
        c.setFillColorRGB(0.8, 0.8, 0.8)
        c.translate(width_pt/2, height_pt/2)
        c.rotate(45)
        c.drawCentredString(0, 0, watermark)
        c.restoreState()

    # Header text (at top left inside margin)
    if header_text:
        c.setFillColorRGB(0, 0, 0)
        if custom_font:
            c.setFont(custom_font, 12)
        else:
            c.setFont("Helvetica", 12)
        c.drawString(left, height_pt - inches_to_points(margins['top']) + 5, header_text)

    # Footer text (at bottom left inside margin)
    if footer_text:
        c.setFillColorRGB(0, 0, 0)
        if custom_font:
            c.setFont(custom_font, 12)
        else:
            c.setFont("Helvetica", 12)
        c.drawString(left, inches_to_points(margins['bottom']) - 15, footer_text)

    # Page number (centered at bottom)
    if add_page_numbers and page_number is not None:
        c.setFillColorRGB(0, 0, 0)
        if custom_font:
            c.setFont(custom_font, 10)
        else:
            c.setFont("Helvetica", 10)
        c.drawCentredString(width_pt / 2, inches_to_points(0.25), str(page_number))

    c.showPage()

def generate_back_cover_page(c, width_pt, height_pt, custom_font=None):
    """
    Generate a simple back cover page with a centered "The End" message.
    """
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, width_pt, height_pt, fill=1)
    c.setFillColorRGB(0, 0, 0)
    if custom_font:
        c.setFont(custom_font, 24)
    else:
        c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width_pt / 2, height_pt / 2, "The End")
    c.showPage()

def generate_pdf(options):
    """
    Generate the PDF using the provided options.
    Returns the output filename if successful.
    """
    try:
        width_pt = inches_to_points(options['width'])
        height_pt = inches_to_points(options['height'])
        margins = {
            'left': options['margin_left'],
            'right': options['margin_right'],
            'top': options['margin_top'],
            'bottom': options['margin_bottom']
        }
        if options['output']:
            output_filename = options['output']
        else:
            safe_title = "".join(c for c in options['title'] if c.isalnum() or c in (" ", "_")).rstrip()
            output_filename = f"{safe_title.replace(' ', '_')}.pdf"

        c = canvas.Canvas(output_filename, pagesize=(width_pt, height_pt))

        # Register custom font if provided
        custom_font = None
        if options['font']:
            if not options['font_name']:
                options['font_name'] = os.path.splitext(os.path.basename(options['font']))[0]
            try:
                pdfmetrics.registerFont(TTFont(options['font_name'], options['font']))
                custom_font = options['font_name']
            except Exception as e:
                messagebox.showwarning("Font Warning", f"Failed to register custom font: {e}")

        generate_cover_page(c, options['title'], options['subtitle'], options['author'],
                            width_pt, height_pt, cover_image=options['cover_image'], custom_font=custom_font)

        for i in range(1, options['pages'] + 1):
            generate_interior_page(c, options['type'], width_pt, height_pt, margins,
                                   line_spacing=options['line_spacing'],
                                   dot_spacing=options['dot_spacing'],
                                   page_number=i if options['page_numbers'] else None,
                                   add_page_numbers=options['page_numbers'],
                                   watermark=options['watermark'],
                                   header_text=options['header_text'],
                                   footer_text=options['footer_text'],
                                   custom_font=custom_font,
                                   grid_spacing=options['grid_spacing'])
        generate_back_cover_page(c, width_pt, height_pt, custom_font=custom_font)
        c.save()
        return output_filename
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during PDF generation:\n{e}")
        return None

# ---------------------------
# Tkinter GUI with Predetermined Templates
# ---------------------------

class BookGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Low-Content Book Generator for Amazon KDP")
        self.templates = {
            "Custom": {},
            "Daily Journal": {
                "title": "Daily Journal",
                "subtitle": "",
                "author": "",
                "pages": 120,
                "width": 6,
                "height": 9,
                "type": "lined",
                "margin_left": 0.5,
                "margin_right": 0.5,
                "margin_top": 0.5,
                "margin_bottom": 0.5,
                "line_spacing": 0.25,
                "dot_spacing": 0.5,
                "grid_spacing": 0.25,
                "page_numbers": True,
                "watermark": "",
                "header_text": "Daily Journal",
                "footer_text": "",
                "cover_image": "",
                "font": "",
                "font_name": "",
                "output": ""
            },
            "Notebook": {
                "title": "Notebook",
                "subtitle": "",
                "author": "",
                "pages": 100,
                "width": 8.5,
                "height": 11,
                "type": "blank",
                "margin_left": 1.0,
                "margin_right": 1.0,
                "margin_top": 1.0,
                "margin_bottom": 1.0,
                "line_spacing": 0.25,
                "dot_spacing": 0.5,
                "grid_spacing": 0.25,
                "page_numbers": False,
                "watermark": "",
                "header_text": "",
                "footer_text": "",
                "cover_image": "",
                "font": "",
                "font_name": "",
                "output": ""
            },
            "Planner": {
                "title": "Daily Planner",
                "subtitle": "",
                "author": "",
                "pages": 150,
                "width": 6,
                "height": 9,
                "type": "grid",
                "margin_left": 0.5,
                "margin_right": 0.5,
                "margin_top": 0.5,
                "margin_bottom": 0.5,
                "line_spacing": 0.25,
                "dot_spacing": 0.5,
                "grid_spacing": 0.25,
                "page_numbers": True,
                "watermark": "",
                "header_text": "Daily Planner",
                "footer_text": "Plan your day!",
                "cover_image": "",
                "font": "",
                "font_name": "",
                "output": ""
            },
            "Dotted Journal": {
                "title": "Dotted Journal",
                "subtitle": "",
                "author": "",
                "pages": 120,
                "width": 6,
                "height": 9,
                "type": "dotted",
                "margin_left": 0.5,
                "margin_right": 0.5,
                "margin_top": 0.5,
                "margin_bottom": 0.5,
                "line_spacing": 0.25,
                "dot_spacing": 0.5,
                "grid_spacing": 0.25,
                "page_numbers": True,
                "watermark": "",
                "header_text": "Dotted Journal",
                "footer_text": "",
                "cover_image": "",
                "font": "",
                "font_name": "",
                "output": ""
            }
        }
        self.create_widgets()

    def create_widgets(self):
        padx, pady = 5, 5

        # Row 0: Template Selection
        ttk.Label(self.root, text="Select Template:").grid(row=0, column=0, sticky="e", padx=padx, pady=pady)
        self.template_var = tk.StringVar(value="Custom")
        self.template_combo = ttk.Combobox(self.root, textvariable=self.template_var,
                                           values=list(self.templates.keys()),
                                           state="readonly", width=20)
        self.template_combo.grid(row=0, column=1, sticky="w", padx=padx, pady=pady)
        self.template_combo.bind("<<ComboboxSelected>>", self.apply_template)

        # Row 1: Book Title
        ttk.Label(self.root, text="Book Title:").grid(row=1, column=0, sticky="e", padx=padx, pady=pady)
        self.title_entry = ttk.Entry(self.root, width=40)
        self.title_entry.grid(row=1, column=1, padx=padx, pady=pady)

        # Row 2: Subtitle
        ttk.Label(self.root, text="Subtitle (optional):").grid(row=2, column=0, sticky="e", padx=padx, pady=pady)
        self.subtitle_entry = ttk.Entry(self.root, width=40)
        self.subtitle_entry.grid(row=2, column=1, padx=padx, pady=pady)

        # Row 3: Author
        ttk.Label(self.root, text="Author (optional):").grid(row=3, column=0, sticky="e", padx=padx, pady=pady)
        self.author_entry = ttk.Entry(self.root, width=40)
        self.author_entry.grid(row=3, column=1, padx=padx, pady=pady)

        # Row 4: Number of Pages
        ttk.Label(self.root, text="Number of Interior Pages:").grid(row=4, column=0, sticky="e", padx=padx, pady=pady)
        self.pages_entry = ttk.Entry(self.root, width=10)
        self.pages_entry.grid(row=4, column=1, sticky="w", padx=padx, pady=pady)
        self.pages_entry.insert(0, "100")

        # Row 5: Page Width
        ttk.Label(self.root, text="Page Width (inches):").grid(row=5, column=0, sticky="e", padx=padx, pady=pady)
        self.width_entry = ttk.Entry(self.root, width=10)
        self.width_entry.grid(row=5, column=1, sticky="w", padx=padx, pady=pady)
        self.width_entry.insert(0, "6")
        # Row 6: Page Height
        ttk.Label(self.root, text="Page Height (inches):").grid(row=6, column=0, sticky="e", padx=padx, pady=pady)
        self.height_entry = ttk.Entry(self.root, width=10)
        self.height_entry.grid(row=6, column=1, sticky="w", padx=padx, pady=pady)
        self.height_entry.insert(0, "9")

        # Row 7: Interior Page Type
        ttk.Label(self.root, text="Interior Page Type:").grid(row=7, column=0, sticky="e", padx=padx, pady=pady)
        self.type_var = tk.StringVar(value="lined")
        self.type_combo = ttk.Combobox(self.root, textvariable=self.type_var,
                                       values=["lined", "dotted", "blank", "grid"],
                                       state="readonly", width=10)
        self.type_combo.grid(row=7, column=1, sticky="w", padx=padx, pady=pady)

        # Row 8-11: Margins
        ttk.Label(self.root, text="Left Margin (inches):").grid(row=8, column=0, sticky="e", padx=padx, pady=pady)
        self.margin_left_entry = ttk.Entry(self.root, width=10)
        self.margin_left_entry.grid(row=8, column=1, sticky="w", padx=padx, pady=pady)
        self.margin_left_entry.insert(0, "0.5")
        ttk.Label(self.root, text="Right Margin (inches):").grid(row=9, column=0, sticky="e", padx=padx, pady=pady)
        self.margin_right_entry = ttk.Entry(self.root, width=10)
        self.margin_right_entry.grid(row=9, column=1, sticky="w", padx=padx, pady=pady)
        self.margin_right_entry.insert(0, "0.5")
        ttk.Label(self.root, text="Top Margin (inches):").grid(row=10, column=0, sticky="e", padx=padx, pady=pady)
        self.margin_top_entry = ttk.Entry(self.root, width=10)
        self.margin_top_entry.grid(row=10, column=1, sticky="w", padx=padx, pady=pady)
        self.margin_top_entry.insert(0, "0.5")
        ttk.Label(self.root, text="Bottom Margin (inches):").grid(row=11, column=0, sticky="e", padx=padx, pady=pady)
        self.margin_bottom_entry = ttk.Entry(self.root, width=10)
        self.margin_bottom_entry.grid(row=11, column=1, sticky="w", padx=padx, pady=pady)
        self.margin_bottom_entry.insert(0, "0.5")

        # Row 12-14: Spacing Options
        ttk.Label(self.root, text="Line Spacing (inches):").grid(row=12, column=0, sticky="e", padx=padx, pady=pady)
        self.line_spacing_entry = ttk.Entry(self.root, width=10)
        self.line_spacing_entry.grid(row=12, column=1, sticky="w", padx=padx, pady=pady)
        self.line_spacing_entry.insert(0, "0.25")
        ttk.Label(self.root, text="Dot Spacing (inches):").grid(row=13, column=0, sticky="e", padx=padx, pady=pady)
        self.dot_spacing_entry = ttk.Entry(self.root, width=10)
        self.dot_spacing_entry.grid(row=13, column=1, sticky="w", padx=padx, pady=pady)
        self.dot_spacing_entry.insert(0, "0.5")
        ttk.Label(self.root, text="Grid Spacing (inches, for grid type):").grid(row=14, column=0, sticky="e", padx=padx, pady=pady)
        self.grid_spacing_entry = ttk.Entry(self.root, width=10)
        self.grid_spacing_entry.grid(row=14, column=1, sticky="w", padx=padx, pady=pady)
        self.grid_spacing_entry.insert(0, "0.25")

        # Row 15: Additional Option (Page Numbers)
        self.page_numbers_var = tk.BooleanVar()
        self.page_numbers_check = ttk.Checkbutton(self.root, text="Include Page Numbers", variable=self.page_numbers_var)
        self.page_numbers_check.grid(row=15, column=0, columnspan=2, padx=padx, pady=pady)

        # Row 16-18: Watermark, Header, Footer
        ttk.Label(self.root, text="Watermark (optional):").grid(row=16, column=0, sticky="e", padx=padx, pady=pady)
        self.watermark_entry = ttk.Entry(self.root, width=40)
        self.watermark_entry.grid(row=16, column=1, padx=padx, pady=pady)
        ttk.Label(self.root, text="Header Text (optional):").grid(row=17, column=0, sticky="e", padx=padx, pady=pady)
        self.header_entry = ttk.Entry(self.root, width=40)
        self.header_entry.grid(row=17, column=1, padx=padx, pady=pady)
        ttk.Label(self.root, text="Footer Text (optional):").grid(row=18, column=0, sticky="e", padx=padx, pady=pady)
        self.footer_entry = ttk.Entry(self.root, width=40)
        self.footer_entry.grid(row=18, column=1, padx=padx, pady=pady)

        # Row 19: Cover Image
        ttk.Label(self.root, text="Cover Image Path (optional):").grid(row=19, column=0, sticky="e", padx=padx, pady=pady)
        self.cover_image_entry = ttk.Entry(self.root, width=40)
        self.cover_image_entry.grid(row=19, column=1, padx=padx, pady=pady)
        self.cover_image_button = ttk.Button(self.root, text="Browse...", command=self.browse_cover_image)
        self.cover_image_button.grid(row=19, column=2, padx=padx, pady=pady)

        # Row 20: Custom Font
        ttk.Label(self.root, text="Custom Font Path (optional):").grid(row=20, column=0, sticky="e", padx=padx, pady=pady)
        self.font_entry = ttk.Entry(self.root, width=40)
        self.font_entry.grid(row=20, column=1, padx=padx, pady=pady)
        self.font_button = ttk.Button(self.root, text="Browse...", command=self.browse_font)
        self.font_button.grid(row=20, column=2, padx=padx, pady=pady)
        ttk.Label(self.root, text="Custom Font Name (optional):").grid(row=21, column=0, sticky="e", padx=padx, pady=pady)
        self.font_name_entry = ttk.Entry(self.root, width=40)
        self.font_name_entry.grid(row=21, column=1, padx=padx, pady=pady)

        # Row 22: Output File
        ttk.Label(self.root, text="Output PDF Filename (optional):").grid(row=22, column=0, sticky="e", padx=padx, pady=pady)
        self.output_entry = ttk.Entry(self.root, width=40)
        self.output_entry.grid(row=22, column=1, padx=padx, pady=pady)
        self.output_button = ttk.Button(self.root, text="Browse...", command=self.browse_output)
        self.output_button.grid(row=22, column=2, padx=padx, pady=pady)

        # Row 23: Generate Button
        self.generate_button = ttk.Button(self.root, text="Generate PDF", command=self.on_generate)
        self.generate_button.grid(row=23, column=0, columnspan=3, pady=10)

    def apply_template(self, event=None):
        selected = self.template_var.get()
        if selected == "Custom":
            return  # Do not change fields
        preset = self.templates.get(selected, {})
        # For each field, update the widget if a preset value is provided.
        if "title" in preset:
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, str(preset["title"]))
        if "subtitle" in preset:
            self.subtitle_entry.delete(0, tk.END)
            self.subtitle_entry.insert(0, str(preset["subtitle"]))
        if "author" in preset:
            self.author_entry.delete(0, tk.END)
            self.author_entry.insert(0, str(preset["author"]))
        if "pages" in preset:
            self.pages_entry.delete(0, tk.END)
            self.pages_entry.insert(0, str(preset["pages"]))
        if "width" in preset:
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(preset["width"]))
        if "height" in preset:
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(preset["height"]))
        if "type" in preset:
            self.type_var.set(preset["type"])
        if "margin_left" in preset:
            self.margin_left_entry.delete(0, tk.END)
            self.margin_left_entry.insert(0, str(preset["margin_left"]))
        if "margin_right" in preset:
            self.margin_right_entry.delete(0, tk.END)
            self.margin_right_entry.insert(0, str(preset["margin_right"]))
        if "margin_top" in preset:
            self.margin_top_entry.delete(0, tk.END)
            self.margin_top_entry.insert(0, str(preset["margin_top"]))
        if "margin_bottom" in preset:
            self.margin_bottom_entry.delete(0, tk.END)
            self.margin_bottom_entry.insert(0, str(preset["margin_bottom"]))
        if "line_spacing" in preset:
            self.line_spacing_entry.delete(0, tk.END)
            self.line_spacing_entry.insert(0, str(preset["line_spacing"]))
        if "dot_spacing" in preset:
            self.dot_spacing_entry.delete(0, tk.END)
            self.dot_spacing_entry.insert(0, str(preset["dot_spacing"]))
        if "grid_spacing" in preset:
            self.grid_spacing_entry.delete(0, tk.END)
            self.grid_spacing_entry.insert(0, str(preset["grid_spacing"]))
        if "page_numbers" in preset:
            self.page_numbers_var.set(preset["page_numbers"])
        if "watermark" in preset:
            self.watermark_entry.delete(0, tk.END)
            self.watermark_entry.insert(0, str(preset["watermark"]))
        if "header_text" in preset:
            self.header_entry.delete(0, tk.END)
            self.header_entry.insert(0, str(preset["header_text"]))
        if "footer_text" in preset:
            self.footer_entry.delete(0, tk.END)
            self.footer_entry.insert(0, str(preset["footer_text"]))
        if "cover_image" in preset:
            self.cover_image_entry.delete(0, tk.END)
            self.cover_image_entry.insert(0, str(preset["cover_image"]))
        if "font" in preset:
            self.font_entry.delete(0, tk.END)
            self.font_entry.insert(0, str(preset["font"]))
        if "font_name" in preset:
            self.font_name_entry.delete(0, tk.END)
            self.font_name_entry.insert(0, str(preset["font_name"]))
        if "output" in preset:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, str(preset["output"]))

    def browse_cover_image(self):
        filename = filedialog.askopenfilename(title="Select Cover Image",
                                              filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
        if filename:
            self.cover_image_entry.delete(0, tk.END)
            self.cover_image_entry.insert(0, filename)

    def browse_font(self):
        filename = filedialog.askopenfilename(title="Select TTF Font", filetypes=[("TTF Files", "*.ttf")])
        if filename:
            self.font_entry.delete(0, tk.END)
            self.font_entry.insert(0, filename)

    def browse_output(self):
        filename = filedialog.asksaveasfilename(title="Save Output PDF", defaultextension=".pdf",
                                                filetypes=[("PDF Files", "*.pdf")])
        if filename:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filename)

    def on_generate(self):
        try:
            options = {
                'title': self.title_entry.get().strip(),
                'subtitle': self.subtitle_entry.get().strip(),
                'author': self.author_entry.get().strip(),
                'pages': int(self.pages_entry.get().strip()),
                'width': float(self.width_entry.get().strip()),
                'height': float(self.height_entry.get().strip()),
                'type': self.type_var.get().strip(),
                'margin_left': float(self.margin_left_entry.get().strip()),
                'margin_right': float(self.margin_right_entry.get().strip()),
                'margin_top': float(self.margin_top_entry.get().strip()),
                'margin_bottom': float(self.margin_bottom_entry.get().strip()),
                'line_spacing': float(self.line_spacing_entry.get().strip()),
                'dot_spacing': float(self.dot_spacing_entry.get().strip()),
                'grid_spacing': float(self.grid_spacing_entry.get().strip()),
                'page_numbers': self.page_numbers_var.get(),
                'watermark': self.watermark_entry.get().strip(),
                'header_text': self.header_entry.get().strip(),
                'footer_text': self.footer_entry.get().strip(),
                'cover_image': self.cover_image_entry.get().strip(),
                'font': self.font_entry.get().strip(),
                'font_name': self.font_name_entry.get().strip(),
                'output': self.output_entry.get().strip()
            }
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
            return

        if not options['title']:
            messagebox.showerror("Input Error", "Book title is required.")
            return
        if options['pages'] <= 0:
            messagebox.showerror("Input Error", "Number of pages must be positive.")
            return
        if options['width'] <= 0 or options['height'] <= 0:
            messagebox.showerror("Input Error", "Page dimensions must be positive numbers.")
            return

        output_filename = generate_pdf(options)
        if output_filename:
            messagebox.showinfo("Success", f"PDF generated successfully:\n{output_filename}")

def main():
    root = tk.Tk()
    app = BookGeneratorGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
