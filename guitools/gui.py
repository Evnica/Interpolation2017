from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from interpolation.interpolator import InterpolationMethod
from guitools.tkentrycomplete import AutocompleteCombobox
from guitools.inputcolumnstojson import ColumnSelector
from interpolation.iohelper import Reader
from interpolation.analysis import Analysis

# root = Tk(): blank main window
# frame = is an invisible rectangle container
# pack(fill=X)  # grows with the window, filling its width
# pack(fill=Y, side=LEFT)  # grows with the window, filling its height
# by default all widgets are placed on top of each other, side=LEFT allows to place them in one row
# bg='red', fg='white' background and foreground colors
# self.QUIT = Button(self, text="QUIT", fg="red", command=root.destroy)
# filename = filedialog.askopenfilename(), pathlabel.config(text=filename)

root = Tk()
root.title("Spatio-Temporal Interpolation")
root.iconbitmap('icon.ico')
header = ['Unknown']


def browse():
    filename = filedialog.askopenfilename()
    set_text(input_file_path_entry, filename)
    reader = Reader(filename)
    header = reader.get_column_names()


def set_text(entry, text):
    entry.delete(0, END)
    entry.insert(0, text)
    return

# top frame with all options, but no control buttons
top_frame = Frame(root, padx=10, pady=10)

interpolation_method_label = Label(top_frame, text='Interpolation Method')
interpolation_method_label.grid(row=0, sticky=E)

available_methods = InterpolationMethod.as_string_sequence()
interpolation_methods_combo = AutocompleteCombobox(top_frame, width=47)
interpolation_methods_combo.set_completion_list(available_methods)
interpolation_methods_combo.focus_set()
interpolation_methods_combo.set(available_methods[0])
interpolation_methods_combo.grid(row=0, column=1, columnspan=2, padx=(10, 0), sticky=W)

input_file_label = Label(top_frame, text="Input File Location")
input_file_label.grid(row=1, column=0, sticky=E)

input_file_path_entry = Entry(top_frame, width=50)
input_file_path_entry.grid(row=1, column=1, columnspan=2, padx=(10, 0), sticky=W)

# last column of the top frame
input_file_browse_btn = Button(top_frame, text="Browse...", command=browse)
input_file_browse_btn.grid(row=1, column=3, padx=(10, 0))

checkbox = Checkbutton(top_frame, text="Transform input data to JSON")
checkbox.grid(row=2, column=1, columnspan=2, sticky=W, padx=(5, 0))





# spinbox = Spinbox(root, from_=0, to=10)
# spinbox.pack()

top_frame.pack()
root.mainloop()
