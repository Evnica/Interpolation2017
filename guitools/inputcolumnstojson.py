from tkinter import *


class ColumnSelector:
    def __init__(self, header):
        self.column_checkboxes = []
        self.column_selector = Tk()
        self.header = header

    def __call__(self):
        if self.header is not None:
            for i in range(len(self.header)):
                self.column_checkboxes.append(Checkbutton(self.column_selector, text=self.header[i]))
            for i in range(len(self.header)):
                self.column_checkboxes[i].pack()
        self.QUIT = Button(self, text="QUIT", fg="red", command=self.column_selector.destroy)
        self.QUIT.pack()
        self.column_selector.mainloop()
