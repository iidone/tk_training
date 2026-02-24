import tkinter as tk
from tkinter import ttk

COLOR_MAIN_BG = "#FFFFFF"     
COLOR_SECONDARY_BG = "#7FFF00"
COLOR_ACCENT = "#00FA9A"      
COLOR_DISCOUNT_BG = "#2E8B57" 
COLOR_TEXT = "#000000"        

FONT_MAIN = ("Times New Roman", 12)
FONT_HEADER = ("Times New Roman", 16)
FONT_TITLE = ("Times New Roman", 20)
FONT_BUTTON = ("Times New Roman", 11)

def create_button(parent, text, command, bg=None, fg=None, width=None):
    btn_bg = bg if bg else COLOR_ACCENT
    btn_fg = fg if fg else COLOR_TEXT
    
    btn = tk.Button(
        parent, 
        text=text, 
        command=command,
        font=FONT_BUTTON,
        bg=btn_bg,
        fg=btn_fg,
        width=width,
        relief=tk.RAISED,
        bd=2
    )
    return btn

def create_label(parent, text, font=None, bg=None, fg=None):
    lbl_font = font if font else FONT_MAIN
    lbl_bg = bg if bg else COLOR_MAIN_BG
    lbl_fg = fg if fg else COLOR_TEXT
    
    return tk.Label(
        parent, 
        text=text, 
        font=lbl_font,
        bg=lbl_bg,
        fg=lbl_fg
    )

def get_discount_bg(discount):
    if discount > 15:
        return COLOR_DISCOUNT_BG
    return COLOR_SECONDARY_BG

def setup_treeview_style():
    style = ttk.Style()
    style.theme_use('clam')
    
    style.configure(
        "Treeview",
        font=FONT_MAIN,
        background=COLOR_MAIN_BG,
        foreground=COLOR_TEXT,
        fieldbackground=COLOR_MAIN_BG,
        rowheight=25
    )
    
    style.configure(
        "Treeview.Heading",
        font=FONT_HEADER,
        background=COLOR_SECONDARY_BG,
        foreground=COLOR_TEXT
    )
    
    style.map(
        "Treeview",
        background=[('selected', COLOR_ACCENT)]
    )
