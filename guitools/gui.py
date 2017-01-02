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


class Gui(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.header = ['Unknown']
        self.initial_to_json_checked = IntVar()
        self.interpolate_checked = IntVar()
        self.output_file = None

        # top frame with all options, but no control buttons
        self.top_frame = Frame(self, padx=10, pady=10)

        # row 0: Interpolation method
        interpolation_method_label = Label(self.top_frame, text='Interpolation Method')
        interpolation_method_label.grid(row=0, sticky=E)
        available_methods = InterpolationMethod.as_string_sequence()
        self.interpolation_methods_combo = AutocompleteCombobox(self.top_frame, width=47)
        self.interpolation_methods_combo.set_completion_list(available_methods)
        self.interpolation_methods_combo.focus_set()
        self.interpolation_methods_combo.set(available_methods[0])
        self.interpolation_methods_combo.bind("<<ComboboxSelected>>", self.update_interpolation_parameters)
        self.interpolation_methods_combo.grid(row=0, column=1, columnspan=2, padx=(10, 0), sticky=W)

        # row 1: Input file
        input_file_label = Label(self.top_frame, text="Input File Location")
        input_file_label.grid(row=1, column=0, sticky=E)
        self.input_file_path_entry = Entry(self.top_frame, width=50)
        self.input_file_path_entry.grid(row=1, column=1, columnspan=2, padx=(10, 0), sticky=W)
        input_file_browse_btn = Button(self.top_frame, text="Browse...", command=self.browse)
        input_file_browse_btn.grid(row=1, column=3, padx=(10, 0))

        # row 2: Checkbox for input data transformation in JSON
        self.checkbox_transform_input = Checkbutton(self.top_frame, text="Transform input data to JSON",
                                                    onvalue=1, offvalue=0, variable=self.initial_to_json_checked)
        self.checkbox_transform_input.grid(row=2, column=1, columnspan=2, sticky=W, padx=(5, 0))

        # rows 3-5: Parameters of input data transformation
        temperature_label = Label(self.top_frame, text="Temperature Column")
        temperature_label.grid(row=3, column=1, sticky=E)
        pressure_label = Label(self.top_frame, text="Pressure Column")
        pressure_label.grid(row=4, column=1, sticky=E)
        humidity_label = Label(self.top_frame, text="Humidity Column")
        humidity_label.grid(row=5, column=1, sticky=E)

        self.temperature_combo = AutocompleteCombobox(self.top_frame, width=28)
        self.temperature_combo.config(state=DISABLED)
        self.temperature_combo.grid(row=3, column=2, sticky=W, padx=(5, 0))

        self.pressure_combo = AutocompleteCombobox(self.top_frame, width=28)
        self.pressure_combo.config(state=DISABLED)
        self.pressure_combo.grid(row=4, column=2, sticky=W, padx=(5, 0))

        self.humidity_combo = AutocompleteCombobox(self.top_frame, width=28)
        self.humidity_combo.config(state=DISABLED)
        self.humidity_combo.grid(row=5, column=2, sticky=W, padx=(5, 0))

        # row 6-9: Interpolation parameters
        self.checkbox_interpolate = Checkbutton(self.top_frame, text="Interpolate input data with the chosen method",
                                                onvalue=1, offvalue=0, variable=self.interpolate_checked,
                                                command=self.check_interpolate)
        self.checkbox_interpolate.grid(row=6, column=1, columnspan=2, sticky=W, padx=(5, 0))

        neighbors_label = Label(self.top_frame, text="Nearest Neighbors")
        neighbors_label.grid(row=7, column=1, sticky=E)
        power_label = Label(self.top_frame, text="Power Value")
        power_label.grid(row=8, column=1, sticky=E)
        function_type_label = Label(self.top_frame, text="RBF Function Type")
        function_type_label.grid(row=9, column=1, sticky=E)

        self.neighbors_spinner = Spinbox(self.top_frame, from_=2, to=25, width=29)
        self.neighbors_spinner.config(state=DISABLED)
        self.neighbors_spinner.grid(row=7, column=2, sticky=W, padx=(5, 0))

        self.power_spinner = Spinbox(self.top_frame, from_=1, to=3, width=29)
        self.power_spinner.config(state=DISABLED)
        self.power_spinner.grid(row=8, column=2, sticky=W, padx=(5, 0))

        self.functions_combo = AutocompleteCombobox(self.top_frame, width=28)
        functions = ['Thin Plate', 'Cubic', 'Linear']
        self.functions_combo.set_completion_list(functions)
        self.functions_combo.set(functions[0])
        self.functions_combo.config(state=DISABLED)
        self.functions_combo.grid(row=9, column=2, sticky=W, padx=(5, 0))

        # row 10 - output file location
        output_file_label = Label(self.top_frame, text="Output File Location")
        output_file_label.grid(row=10, column=0, sticky=E)
        self.output_file_path_entry = Entry(self.top_frame, width=50)
        self.output_file_path_entry.grid(row=10, column=1, columnspan=2, padx=(10, 0), sticky=W)
        self.output_file_browse_btn = Button(self.top_frame, text="Browse...", command=self.save)
        self.output_file_browse_btn.grid(row=10, column=3, padx=(10, 0))

        self.top_frame.pack()

    def check_interpolate(self):
        if self.interpolate_checked.get() == 1:
            self.activate_appropriate_parameters()
        else:
            self.power_spinner.config(state=DISABLED)
            self.neighbors_spinner.config(state=DISABLED)
            self.functions_combo.config(state=DISABLED)

    def update_interpolation_parameters(self, event):
        if self.interpolate_checked.get() == 1:
            self.activate_appropriate_parameters()

    def activate_appropriate_parameters(self):
        if 'IDW' in self.interpolation_methods_combo.get():
            self.power_spinner.config(state=NORMAL)
            self.neighbors_spinner.config(state=NORMAL)
            self.functions_combo.config(state=DISABLED)
        else:
            self.power_spinner.config(state=DISABLED)
            self.neighbors_spinner.config(state=DISABLED)
            self.functions_combo.config(state=NORMAL)

    def browse(self):
        filename = filedialog.askopenfilename()
        self.set_text(self.input_file_path_entry, filename)
        reader = Reader(filename)
        self.header = reader.get_column_names()
        values = []
        for i in range(len(self.header)):
            if 'pres' in self.header[i] or 'temp' in self.header[i] or 'hum' in self.header[i]:
                values.append(self.header[i])
        self.temperature_combo.set_completion_list(values)
        self.pressure_combo.set_completion_list(values)
        self.humidity_combo.set_completion_list(values)
        temp_set = False
        pres_set = False
        hum_set = False
        for i in range(len(values)):
            if 'temp' in values[i] and not temp_set:
                self.temperature_combo.set(values[i])
                temp_set = True
                continue
            if 'pres' in values[i] and not pres_set:
                self.pressure_combo.set(values[i])
                pres_set = True
                continue
            if 'hum' in values[i] and not hum_set:
                self.humidity_combo.set(values[i])
                hum_set = True
        if self.initial_to_json_checked.get() == 1:
            self.temperature_combo.config(state=ACTIVE)
            self.pressure_combo.config(state=ACTIVE)
            self.humidity_combo.config(state=ACTIVE)

    def save(self):
        self.output_file = filedialog.asksaveasfilename(defaultextension='.json')
        if self.output_file is None:
            return
        else:
            self.set_text(self.output_file_path_entry, self.output_file)

    @staticmethod
    def set_text(entry, text):
        entry.delete(0, END)
        entry.insert(0, text)
        return


def start():
    root = Tk()
    root.title("Spatio-Temporal Interpolation")
    root.iconbitmap('icon.ico')
    content = Gui()
    content.pack()
    root.mainloop()


if __name__ == '__main__':
    start()




# spinbox = Spinbox(root, from_=0, to=10)
# spinbox.pack()

