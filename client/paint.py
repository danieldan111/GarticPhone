import tkinter as tk
import PIL
import PIL.ImageDraw
from tkinter import colorchooser


WHITE = (255, 255, 255)


class PaintGUI:
    def __init__(self, width, height, root):
        self.width = width
        self.height = height
        self.root = root
        
        self.brush_width = 5
        self.current_color = "#000000"

        self.cnv = tk.Canvas(self.root, width=self.width - 10, height=self.height - 10, bg="white")
        self.cnv.pack()
        self.cnv.bind("<B1-Motion>", self.paint)
    
        self.image = PIL.Image.new("RGB", (self.width, self.height), WHITE)
        self.draw = PIL.ImageDraw.Draw(self.image)
        self.can_draw = True

        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack(fill="x")

        self.btn_frame.columnconfigure(0, weight=1)
        self.btn_frame.columnconfigure(1, weight=1)
        # self.btn_frame.columnconfigure(2, weight=1)

        self.clear_btn = tk.Button(self.btn_frame, text="Clear", command=self.clear, font=("Arial", 15), width=15)
        self.clear_btn.grid(row=0, column=1, sticky=tk.W + tk.E)

        # self.save_btn = tk.Button(self.btn_frame, text="Save", command=self.save)
        # self.save_btn.grid(row=0, column=2, sticky=tk.W + tk.E)

        self.bplus_btn = tk.Button(self.btn_frame, text="Increase Brush Size", command=self.brush_plus, font=("Arial", 15))
        self.bplus_btn.grid(row=0, column=0, sticky=tk.W + tk.E)

        self.bminus_btn = tk.Button(self.btn_frame, text="Decrease Brush Size", command=self.brush_minus, font=("Arial", 15))
        self.bminus_btn.grid(row=1, column=0, sticky=tk.W + tk.E)

        self.color_btn = tk.Button(self.btn_frame, text="Change Color", command=self.change_color, font=("Arial", 15))
        self.color_btn.grid(row=1, column=1, sticky=tk.W + tk.E)


        # self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        # self.root.mainloop()

    def paint(self, event):
        if self.can_draw:
            x1, y1 = (event.x - 1), (event.y - 1)
            x2, y2 = (event.x + 1), (event.y + 1)
            self.cnv.create_rectangle(x1, y1, x2, y2, outline=self.current_color, fill=self.current_color, width=self.brush_width)
            self.draw.rectangle([x1, y1, x2 + self.brush_width, y2 + self.brush_width], outline=self.current_color, fill=self.current_color, width=self.brush_width)


    def clear(self):
        self.cnv.delete("all")
        self.draw.rectangle([0, 0, 1000, 1000], fill="white")


    
    def brush_plus(self):
        self.brush_width += 1


    def brush_minus(self):
        if self.brush_width > 1:
            self.brush_width -= 1


    def change_color(self):
        _, self.current_color = colorchooser.askcolor(title="Choose a color")
    

    def disable_draw(self):
        self.can_draw = False
        self.clear_btn.config(state="disabled")
        self.bplus_btn.config(state="disabled")
        self.bminus_btn.config(state="disabled")
        self.color_btn.config(state="disabled")
   


if __name__ == "__main__":
    PaintGUI()