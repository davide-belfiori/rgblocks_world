from tkinter import Frame, Canvas, ttk, LEFT, BOTH, Y
from tkinter.constants import RIGHT

class ScrollableFrame(Frame):
    def __init__(self, container, bg_color = "white", width = 200, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = Canvas(self, bd=0, highlightthickness=0, background=bg_color, width=width)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = Frame(canvas, background=bg_color, padx=5)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)