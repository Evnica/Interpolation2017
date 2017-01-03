from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from interpolation.interpolator import InterpolationMethod
from guitools.tkentrycomplete import AutocompleteCombobox
from guitools.inputcolumnstojson import ColumnSelector
from interpolation.iohelper import Reader
from interpolation.analysis import Analysis
from PIL import Image, ImageTk
from io import BytesIO
import base64

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
        self.file_chosen = False
        self.filename = None
        self.file_chosen = False

        # top frame with all options, but no control buttons
        self.top_frame = Frame(self, padx=20, pady=20)

        # row 0: Interpolation method
        interpolation_method_label = Label(self.top_frame, text='Interpolation Method')
        interpolation_method_label.grid(row=0, sticky=E)
        available_methods = InterpolationMethod.as_string_sequence()
        self.interpolation_methods_combo = AutocompleteCombobox(self.top_frame, width=47)
        self.interpolation_methods_combo.set_completion_list(available_methods)
        self.interpolation_methods_combo.focus_set()
        self.interpolation_methods_combo.set(available_methods[0])
        self.interpolation_methods_combo.bind("<<ComboboxSelected>>", self.change_in_interpolation_combo)
        self.interpolation_methods_combo.grid(row=0, column=1, columnspan=2, padx=(10, 0), sticky=W)

        # row 1: Input file
        input_file_label = Label(self.top_frame, text="Input File Location")
        input_file_label.grid(row=1, column=0, sticky=E)
        self.input_file_path_entry = Entry(self.top_frame, width=50)
        self.input_file_path_entry.grid(row=1, column=1, columnspan=2, padx=(10, 0), sticky=W)
        input_file_browse_btn = Button(self.top_frame, text="Browse...", command=self.browse)
        input_file_browse_btn.grid(row=1, column=3, padx=(9, 0))

        # row 2: Checkbox for input data transformation in JSON
        self.checkbox_transform_input = Checkbutton(self.top_frame, text="Transform input data to JSON",
                                                    onvalue=1, offvalue=0, variable=self.initial_to_json_checked,
                                                    command=self.check_to_json)
        self.checkbox_transform_input.grid(row=2, column=1, columnspan=2, sticky=W, padx=(5, 0))

        # rows 3-5: Parameters of input data transformation
        temperature_label = Label(self.top_frame, text="Temperature Column")
        temperature_label.grid(row=3, column=1, sticky=E)
        pressure_label = Label(self.top_frame, text="Pressure Column")
        pressure_label.grid(row=4, column=1, sticky=E)
        humidity_label = Label(self.top_frame, text="Humidity Column")
        humidity_label.grid(row=5, column=1, sticky=E)

        self.temperature_combo = AutocompleteCombobox(self.top_frame, width=22)
        self.temperature_combo.config(state=DISABLED)
        self.temperature_combo.grid(row=3, column=2, sticky=W, padx=(5, 0))

        self.pressure_combo = AutocompleteCombobox(self.top_frame, width=22)
        self.pressure_combo.config(state=DISABLED)
        self.pressure_combo.grid(row=4, column=2, sticky=W, padx=(5, 0))

        self.humidity_combo = AutocompleteCombobox(self.top_frame, width=22)
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

        self.neighbors_spinner = Spinbox(self.top_frame, from_=2, to=25, width=23)
        self.neighbors_spinner.config(state=DISABLED)
        self.neighbors_spinner.grid(row=7, column=2, sticky=W, padx=(5, 0))

        self.power_spinner = Spinbox(self.top_frame, from_=1, to=3, width=23)
        self.power_spinner.config(state=DISABLED)
        self.power_spinner.grid(row=8, column=2, sticky=W, padx=(5, 0))

        self.functions_combo = AutocompleteCombobox(self.top_frame, width=22)
        functions = ['Thin Plate', 'Cubic', 'Linear']
        self.functions_combo.set_completion_list(functions)
        self.functions_combo.set(functions[0])
        self.functions_combo.config(state=DISABLED)
        self.functions_combo.grid(row=9, column=2, sticky=W, padx=(5, 0))

        # row 10 - output file location
        output_file_label = Label(self.top_frame, text="Output File Location")
        output_file_label.grid(row=10, column=0, sticky=E, pady=(0, 7))
        self.output_file_path_entry = Entry(self.top_frame, width=50)
        self.output_file_path_entry.grid(row=10, column=1, columnspan=2, padx=(10, 0), pady=(0, 5), sticky=W)
        self.output_file_browse_btn = Button(self.top_frame, text="Browse...", command=self.save)
        self.output_file_browse_btn.grid(row=10, column=3, padx=(9, 0), pady=(0, 5))

        # row 11-14 column names
        parameters_label = Label(self.top_frame, text='Parameter columns: Latitude')
        parameters_label.grid(row=11, column=0, sticky=E)
        self.lat_combo = AutocompleteCombobox(self.top_frame, width=17)
        # self.parameters_combo.bind("<<ComboboxSelected>>", )
        self.lat_combo.grid(row=11, column=1, padx=(10, 0), sticky=W)
        self.lat_combo.config(state=DISABLED)

        lon_label = Label(self.top_frame, text='Longitude')
        lon_label.grid(row=12, column=0, sticky=E)
        self.lon_combo = AutocompleteCombobox(self.top_frame, width=17)
        # self.lon_combo.bind("<<ComboboxSelected>>", )
        self.lon_combo.grid(row=12, column=1, padx=(10, 0), sticky=W)
        self.lon_combo.config(state=DISABLED)

        alt_label = Label(self.top_frame, text='Altitude')
        alt_label.grid(row=13, column=0, sticky=E)
        self.alt_combo = AutocompleteCombobox(self.top_frame, width=17)
        # self.lon_combo.bind("<<ComboboxSelected>>", )
        self.alt_combo.grid(row=13, column=1, padx=(10, 0), sticky=W)
        self.alt_combo.config(state=DISABLED)

        value_label = Label(self.top_frame, text='Interpolation Value')
        value_label.grid(row=14, column=0, sticky=E)
        self.value_combo = AutocompleteCombobox(self.top_frame, width=17)
        # self.lon_combo.bind("<<ComboboxSelected>>", )
        self.value_combo.grid(row=14, column=1, padx=(10, 0), sticky=W)
        self.value_combo.config(state=DISABLED)

        self.param_frame = Frame(self.top_frame)
        time_label = Label(self.param_frame, text='Timestamp')
        time_label.grid(row=0, column=0, sticky=E, padx=(10, 1))
        self.time_combo = AutocompleteCombobox(self.param_frame, width=17)
        # self.parameters_combo.bind("<<ComboboxSelected>>", )
        self.time_combo.grid(row=0, column=1, padx=(10, 0), sticky=W)
        self.time_combo.config(state=DISABLED)

        density_label = Label(self.param_frame, text='Spatial Density')
        density_label.grid(row=1, column=0, sticky=E, padx=(10, 1))
        self.density_spinner = Spinbox(self.param_frame, from_=1, to=25, width=18)
        self.density_spinner.grid(row=1, column=1, padx=(10, 0), sticky=W)
        self.density_spinner.config(state=DISABLED)

        max_temporal_step = self.calc_max_temporal_step()

        temporal_step_label = Label(self.param_frame, text='Temporal Density')
        temporal_step_label.grid(row=2, column=0, sticky=E, padx=(5, 1))
        self.temporal_step_spinner = Spinbox(self.param_frame, from_=1, to=max_temporal_step, width=18)
        self.temporal_step_spinner.grid(row=2, column=1, padx=(10, 0), sticky=W)
        self.temporal_step_spinner.config(state=DISABLED)

        self.param_frame.grid(row=11, column=2, columnspan=2, rowspan=3)

        self.info_button = Button(self.top_frame, text="About...")
        self.info_button.grid(row=15, column=0, pady=(15, 0), columnspan=2, sticky=W)

        self.calc_button = Button(self.top_frame, text="Execute", width=20)
        self.calc_button.grid(row=15, column=2, pady=(15, 0), columnspan=2, sticky=E)
        self.calc_button.config(state=DISABLED)

        self.top_frame.pack()

    def calc_max_temporal_step(self):
        return 300

    def add_column_names_to_combo(self, combo, i):
        combo.set_completion_list(self.header)
        combo.set(self.header[i])

    def check_to_json(self):
        if self.initial_to_json_checked.get() == 1 and self.file_chosen:
            self.input_to_json_on()
        else:
            self.input_to_json_off()

    def check_interpolate(self):
        if self.interpolate_checked.get() == 1 and self.file_chosen:
            self.update_interface_for_interpolation_method()
        else:
            self.disable_all_interpolation_parameters()

    def change_in_interpolation_combo(self, event):
        if self.interpolate_checked.get() == 1 and self.file_chosen:
            self.update_interface_for_interpolation_method()

    def update_interface_for_interpolation_method(self):
        if 'IDW: Spatial' in self.interpolation_methods_combo.get():
            self.spatial_idw_state()
        elif 'IDW: Spatio' in self.interpolation_methods_combo.get():
            self.spatio_temporal_idw_state()
        elif 'RBF: Spatial' in self.interpolation_methods_combo.get():
            self.spatial_rbf_state()
        else:
            self.spatio_temporal_rbf_state()

    def suitable_file_chosen(self):
        if self.filename is not None:
            try:
                reader = Reader(self.filename)
                self.header = reader.get_column_names()
                lat_in = False
                lon_in = False
                alt_in = False
                proper_header = False
                for i in range(len(self.header)):
                    if 'lat' in self.header[i]:
                        lat_in = True
                    if 'lon' in self.header[i]:
                        lon_in = True
                    if 'alt' in self.header[i]:
                        alt_in = True
                    if lat_in and lon_in and alt_in:
                        proper_header = True
                        break
                if not proper_header:
                    self.header = []
                    self.show_load_file_error()
                    self.file_chosen = False
                    return False
                else:
                    self.file_chosen = True
                    return True
            except:
                self.header = []
                self.show_load_file_error()
                self.file_chosen = False
                return False
        else:
            self.file_chosen = False
            return False

    def browse(self):
        self.filename = filedialog.askopenfilename()
        self.set_text(self.input_file_path_entry, self.filename)
        if self.suitable_file_chosen():
            values = []
            for i in range(len(self.header)):
                if 'pres' in self.header[i] or 'temp' in self.header[i] or 'hum' in self.header[i]:
                    values.append(self.header[i])
            self.temperature_combo.set_completion_list(values)
            self.pressure_combo.set_completion_list(values)
            self.humidity_combo.set_completion_list(values)
            self.lat_combo.set_completion_list(self.header)
            self.lon_combo.set_completion_list(self.header)
            self.alt_combo.set_completion_list(self.header)
            self.value_combo.set_completion_list(self.header)
            self.time_combo.set_completion_list(self.header)
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
            self.lat_combo.set(self.header[2])
            self.lon_combo.set(self.header[3])
            self.alt_combo.set(self.header[4])
            self.value_combo.set(self.header[13])
            self.time_combo.set(self.header[1])

            if self.initial_to_json_checked.get() == 1:
                self.input_to_json_on()
            if self.interpolate_checked.get() == 1:
                self.update_interface_for_interpolation_method()
        else:
            self.initial_to_json_checked.set(0)
            self.input_to_json_off()
            self.temperature_combo.set_completion_list([''])
            self.temperature_combo.set('')
            self.pressure_combo.set_completion_list([''])
            self.pressure_combo.set('')
            self.humidity_combo.set_completion_list([''])
            self.humidity_combo.set('')
            self.interpolate_checked.set(0)
            self.disable_all_interpolation_parameters()
            self.calc_button.config(state=DISABLED)

    def save(self):
        self.output_file = filedialog.asksaveasfilename(defaultextension='.json')
        if self.output_file is None:
            return
        else:
            self.set_text(self.output_file_path_entry, self.output_file)

    @staticmethod
    def show_load_file_error():
        messagebox.showerror('File Load Error', "Chosen file has wrong format \nand can't be processed")

    @staticmethod
    def set_text(entry, text):
        entry.delete(0, END)
        entry.insert(0, text)
        return

    def spatial_idw_state(self):
        self.neighbors_spinner.config(state=NORMAL)
        self.power_spinner.config(state=NORMAL)
        self.functions_combo.config(state=DISABLED)
        self.lat_combo.config(state=ACTIVE)
        self.lon_combo.config(state=ACTIVE)
        self.alt_combo.config(state=ACTIVE)
        self.value_combo.config(state=ACTIVE)
        self.time_combo.config(state=ACTIVE)
        self.density_spinner.config(state=NORMAL)
        self.temporal_step_spinner.config(state=DISABLED)
        self.calc_button.config(state=ACTIVE)

    def spatio_temporal_idw_state(self):
        self.neighbors_spinner.config(state=NORMAL)
        self.power_spinner.config(state=NORMAL)
        self.functions_combo.config(state=DISABLED)
        self.lat_combo.config(state=ACTIVE)
        self.lon_combo.config(state=ACTIVE)
        self.alt_combo.config(state=ACTIVE)
        self.value_combo.config(state=ACTIVE)
        self.time_combo.config(state=ACTIVE)
        self.density_spinner.config(state=NORMAL)
        self.temporal_step_spinner.config(state=NORMAL)
        self.calc_button.config(state=ACTIVE)

    def spatio_temporal_rbf_state(self):
        self.neighbors_spinner.config(state=DISABLED)
        self.power_spinner.config(state=DISABLED)
        self.functions_combo.config(state=ACTIVE)
        self.lat_combo.config(state=ACTIVE)
        self.lon_combo.config(state=ACTIVE)
        self.alt_combo.config(state=ACTIVE)
        self.value_combo.config(state=ACTIVE)
        self.time_combo.config(state=ACTIVE)
        self.density_spinner.config(state=NORMAL)
        self.temporal_step_spinner.config(state=NORMAL)
        self.calc_button.config(state=ACTIVE)

    def spatial_rbf_state(self):
        self.neighbors_spinner.config(state=DISABLED)
        self.power_spinner.config(state=DISABLED)
        self.functions_combo.config(state=ACTIVE)
        self.lat_combo.config(state=ACTIVE)
        self.lon_combo.config(state=ACTIVE)
        self.alt_combo.config(state=ACTIVE)
        self.value_combo.config(state=ACTIVE)
        self.time_combo.config(state=ACTIVE)
        self.density_spinner.config(state=NORMAL)
        self.temporal_step_spinner.config(state=DISABLED)
        self.calc_button.config(state=ACTIVE)

    def input_to_json_on(self):
        self.temperature_combo.config(state=ACTIVE)
        self.pressure_combo.config(state=ACTIVE)
        self.humidity_combo.config(state=ACTIVE)
        self.calc_button.config(state=ACTIVE)

    def input_to_json_off(self):
        self.temperature_combo.config(state=DISABLED)
        self.pressure_combo.config(state=DISABLED)
        self.humidity_combo.config(state=DISABLED)
        if self.interpolate_checked.get() == 0:
            self.calc_button.config(state=DISABLED)

    def disable_all_interpolation_parameters(self):
        self.neighbors_spinner.config(state=DISABLED)
        self.power_spinner.config(state=DISABLED)
        self.functions_combo.config(state=DISABLED)
        self.lat_combo.config(state=DISABLED)
        self.lon_combo.config(state=DISABLED)
        self.alt_combo.config(state=DISABLED)
        self.value_combo.config(state=DISABLED)
        self.time_combo.config(state=DISABLED)
        self.density_spinner.config(state=DISABLED)
        self.temporal_step_spinner.config(state=DISABLED)
        if self.initial_to_json_checked.get() == 0:
            self.calc_button.config(state=DISABLED)

def start():
    root = Tk()
    root.title("Spatio-Temporal Interpolation")
    root.iconbitmap('icon.ico')
    content = Gui()
    content.pack()
    root.mainloop()
if __name__ == '__main__':
    start()
