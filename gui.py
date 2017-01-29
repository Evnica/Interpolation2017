from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import ntpath
import time
from interpolation.interpolator import interpolate_with_idw, interpolate_with_rbf
from interpolation.interpolator import InterpolationMethod
from interpolation.qualityassessment import access_quality_of_interpolation
from guitools.tkentrycomplete import AutocompleteCombobox
from interpolation.iohelper import Reader, Writer
from interpolation.analysis import Analysis
from interpolation.csvconverter import CsvConverter
from interpolation.utils import TimeHandler
from interpolation.utils import divide_in_random, info


class Gui(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.header = ['Unknown']
        self.initial_to_json_checked = IntVar()
        self.interpolate_checked = IntVar()
        self.output_file = None
        self.file_chosen = False
        self.input_path = None
        self.file_chosen = False
        self.reader = None
        self.analysis = None
        self.csv_converter = None
        self.max_temporal_step = 86400  # default maximum of 24 hours
        self.neighbors_edited = False
        self.power_edited = False
        self.density_edited = False
        self.temporal_step_edited = False
        self.timescale = 1
        self.timescale_edited = False

        # top frame with all options, but no control buttons
        self.top_frame = Frame(self, padx=20, pady=20)

        # row 0: Interpolation method
        interpolation_method_label = Label(self.top_frame, text='Interpolation Method')
        interpolation_method_label.grid(row=0, sticky=E)
        available_methods = InterpolationMethod.as_string_sequence()
        self.interpolation_methods_combo = AutocompleteCombobox(self.top_frame, width=47)
        self.interpolation_methods_combo.set_completion_list(available_methods)
        # self.interpolation_methods_combo.focus_set()
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
        input_file_browse_btn.focus_set()

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

        neighbor_spinner_var = StringVar(self)
        neighbor_spinner_var.set('6')
        self.neighbors_spinner = Spinbox(self.top_frame, from_=2, to=50, width=23, textvariable=neighbor_spinner_var)
        self.neighbors_spinner.config(state=DISABLED)
        self.neighbors_spinner.grid(row=7, column=2, sticky=W, padx=(5, 0))

        power_spinner_var = StringVar(self)
        power_spinner_var.set('2')
        self.power_spinner = Spinbox(self.top_frame, from_=1, to=3, width=23, textvariable=power_spinner_var)
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
        density_spinner_var = StringVar(self)
        density_spinner_var.set('10')
        self.density_spinner = Spinbox(self.param_frame, from_=1, to=50, width=18, textvariable=density_spinner_var)
        self.density_spinner.grid(row=1, column=1, padx=(10, 0), sticky=W)
        self.density_spinner.config(state=DISABLED)

        temporal_step_label = Label(self.param_frame, text='Temporal Density')
        temporal_step_label.grid(row=2, column=0, sticky=E, padx=(5, 1))
        self.temporal_step_spinner = Spinbox(self.param_frame, from_=2, to=86400, width=18)
        self.temporal_step_spinner.grid(row=2, column=1, padx=(10, 0), sticky=W)
        self.temporal_step_spinner.config(state=DISABLED)
        timescale_label = Label(self.param_frame, text='Time Scale')
        timescale_label.grid(row=3, column=0, sticky=E, padx=(5, 1))
        self.timescale_spinner = Spinbox(self.param_frame, from_=0, to=100000, width=18)
        self.timescale_spinner.grid(row=3, column=1, padx=(10, 0), sticky=W)
        self.timescale_spinner.config(state=DISABLED)

        self.param_frame.grid(row=11, column=2, columnspan=2, rowspan=4)

        self.info_button = Button(self.top_frame, text="About...", command=self.info)
        self.info_button.grid(row=15, column=0, pady=(15, 0), columnspan=2, sticky=W)

        self.calc_button = Button(self.top_frame, text="Execute", width=20, command=self.execute)
        self.calc_button.grid(row=15, column=2, pady=(15, 0), columnspan=2, sticky=E)
        self.calc_button.config(state=DISABLED)

        self.top_frame.pack()

    def calc_max_temporal_step(self):
        try:
            self.csv_converter = CsvConverter(self.input_path)
            self.csv_converter(1, 2, 3, 4, 13, 15, 14)
            if len(self.csv_converter.times) > 0:
                try:
                    time_handler = TimeHandler(self.csv_converter.times)
                    self.max_temporal_step = time_handler.get_unix_time_in_seconds(self.csv_converter.time_max) \
                        - time_handler.get_unix_time_in_seconds(self.csv_converter.time_min)
                except:
                    self.max_temporal_step = 60 * 60 * 24
            elif len(self.csv_converter.system_times) > 0:
                self.max_temporal_step = self.csv_converter.time_max - self.csv_converter.time_min
            else:
                self.max_temporal_step = 60 * 60 * 24  # 24 hours maximum
        except:
            self.max_temporal_step = 60 * 60 * 24  # 24 hours maximum
        return self.max_temporal_step

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
        if self.input_path is not None:
            try:
                self.reader = Reader(self.input_path)
                self.header = self.reader.get_column_names()
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
        self.input_path = filedialog.askopenfilename(defaultextension='.csv',
                                                     filetypes=[('Comma Separated Value Files', '*.csv')])
        self.set_text(self.input_file_path_entry, self.input_path)
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

            self.temporal_step_spinner.config(to=self.calc_max_temporal_step())

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
        self.output_file = filedialog.asksaveasfilename(defaultextension='.json',
                                                        filetypes=[('JavaScript Object Notation', '*.json'),
                                                                   ('All files', '*.*')])
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
        self.timescale_spinner.config(state=DISABLED)
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
        self.timescale_spinner.config(state=NORMAL)
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
        self.timescale_spinner.config(state=NORMAL)
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
        self.timescale_spinner.config(state=DISABLED)
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
        self.timescale_spinner.config(state=DISABLED)
        if self.initial_to_json_checked.get() == 0:
            self.calc_button.config(state=DISABLED)

    def execute(self):
        if self.output_file is not None:
            show_statistics = None
            if self.initial_to_json_checked.get() == 1 and self.interpolate_checked.get() == 1:
                self.transform_initial()
                messagebox.showinfo('Converted to JSON', self.inform_transformed_to_json(self.csv_converter))
                self.interpolate()
                message = self.inform_interpolated() + '\n' + self.inform_parameters_set_to_default() + \
                          '\n' + 'Do you want to calculate interpolation error? '
                show_statistics = messagebox.askyesno('Interpolated', message)
            elif self.initial_to_json_checked.get() == 1:
                self.transform_initial()
                messagebox.showinfo('Converted to JSON', self.inform_transformed_to_json(self.csv_converter))
            elif self.interpolate_checked.get() == 1:
                self.interpolate()
                message = self.inform_interpolated() + '\n' + self.inform_parameters_set_to_default() + \
                                                       '\n' + 'Do you want to calculate interpolation error? '
                show_statistics = messagebox.askyesno('Interpolated', message)
            if show_statistics is not None:
                if show_statistics:
                    if len(self.reader.times) > 0:
                        times = self.reader.times
                    else:
                        times = self.reader.system_times
                    if self.analysis.dimension == 3:
                        grouped_samples, one_sample = divide_in_random(10, self.reader.points,
                                                                       self.reader.values, times)
                    else:
                        time_handler = TimeHandler(times)
                        points4d = time_handler.raise_to_fourth_dimension\
                            (points3d=self.reader.points, time_scale=self.timescale)
                        grouped_samples, one_sample = divide_in_random(num_of_random_samples=10, points=points4d,
                                                                       values=self.reader.values, timestamps=times,
                                                                       point_dimension=4)
                    if 'idw' in self.analysis.interpolation_method:
                        mae, mse, rmse, mare, r2 = \
                            access_quality_of_interpolation(grouped_samples=grouped_samples,
                                                            one_sample=one_sample,
                                                            function='idw',
                                                            number_of_neighbors=self.analysis.nearest_neighbors,
                                                            power=self.analysis.power, r2formula='keller')
                    else:
                        mae, mse, rmse, mare, r2 = \
                            access_quality_of_interpolation(grouped_samples=grouped_samples,
                                                            one_sample=one_sample, function='rbf',
                                                            function_type=self.analysis.function,
                                                            r2formula='keller')
                    messagebox.showinfo('Statistics', self.statistics_to_string(mae, mse, rmse, mare, r2,
                                                                                self.analysis.interpolated_total,
                                                                                self.analysis.interpolated_within_range)
                                        )
            self.reader = None
            self.analysis = None
            self.all_edited_parameter_flag_to_false()
        else:
            messagebox.showerror('Choose output file', 'Please select an output file location and name to proceed.')

    def transform_initial(self):
        self.config(cursor='wait')
        temp_name = self.temperature_combo.get().strip()
        press_name = self.pressure_combo.get().strip()
        hum_name = self.humidity_combo.get().strip()
        num_of_correct_fields = 0
        temp_index = 13
        hum_index = 15
        press_index = 14
        if temp_name in self.header[13]:
            num_of_correct_fields += 1
        else:
            for i in range(len(self.header)):
                if temp_name in self.header[i]:
                    temp_index = i
                    break
        if press_name in self.header[14]:
            num_of_correct_fields += 1
        else:
            for i in range(len(self.header)):
                if press_name in self.header[i]:
                    press_index = i
                    break
        if hum_name in self.header[15]:
            num_of_correct_fields += 1
        else:
            for i in range(len(self.header)):
                if hum_name in self.header[i]:
                    hum_index = i
        if num_of_correct_fields != 3:
            if self.file_chosen:
                try:
                    self.csv_converter = CsvConverter(self.input_path)
                    self.csv_converter(1, 2, 3, 4, temp_index, hum_index, press_index)
                except:
                    self.show_load_file_error()
        current_seconds = str(time.time()).replace('.', '')
        if self.output_file is None:
            # default output name is input name + to_json + time in seconds
            self.output_file = self.extract_filename(self.input_path)[:-4] + '_to_json_' \
                               + current_seconds + '.json'
        elif self.interpolate_checked.get() == 1:
            if len(self.output_file) > 31 and 'to_json_' in self.output_file:
                # if the output name was automatically generated in the last execution
                self.output_file = self.output_file[:-31] + '_to_json_' + current_seconds + '.json'
            else:
                self.output_file = self.output_file[:-5] + '_to_json_' + current_seconds + '.json'
        writer = Writer(self.output_file)
        writer.initial_to_json(csv_converter=self.csv_converter)
        self.update()
        self.config(cursor='')
        self.inform_transformed_to_json(self.csv_converter)

    @staticmethod
    def statistics_to_string(mae, mse, rmse, mare, r2, num_of_interpolated, num_within_range):
        return 'Mean Absolute Error: ' + format(mae, '.3f') + \
               '\nMean Square Error: ' + format(mse, '.3f') + \
               '\nRoot Mean Square Error: ' + format(rmse, '.3f') + \
               '\nMean Absolute Relative Error: ' + format(mare, '.3f') + \
               '\nCoefficient of Determination (R^2): ' + format(r2, '.3f') + \
               '\nInterpolated values within input range:\n' + format((num_within_range/num_of_interpolated*100),
                                                                      '.2f') + \
               '% (' + str(num_within_range) + ' of ' + str(num_of_interpolated) + ')'

    def inform_transformed_to_json(self, converter):
        input_for_notification = self.extract_filename(self.input_path)
        try:
            dates = 'Start: ' + '{0:%d.%m.%Y %H:%M:%S}'.format(converter.time_min) + '\n'\
                    'End: ' + '{0:%d.%m.%Y %H:%M:%S}'.format(converter.time_max) + '\n'
        except ValueError:
            dates = 'Start: ' + str(converter.time_min) + '"\n'\
                    'End: ' + str(converter.time_max) + '"\n'
        return 'File ' + input_for_notification + ' was successfully converted to JSON ' + 'and saved under :\n' + \
            self.output_file + '\n\nNumber of observations: ' + str(len(converter.lat_values)) + '\n' \
            'Latitude: from ' + str(converter.lat_min) + ' to ' + str(converter.lat_max) + '\n' \
            'Longitude: from ' + str(converter.lon_min) + ' to ' + str(converter.lon_max) + '\n' \
            'Altitude: from ' + str(converter.alt_min) + ' to ' + str(converter.alt_max) + '\n' + dates + \
            'Temperature: from ' + str(converter.temp_min) + ' to ' + str(converter.temp_max) + '\n' \
            'Humidity: from ' + str(converter.hum_min) + ' to ' + str(converter.hum_max) + '\n' \
            'Pressure: from ' + str(converter.press_min) + ' to ' + str(converter.press_max) + '\n'

    def inform_interpolated(self):
        input_for_notification = self.extract_filename(self.input_path)
        try:
            dates = 'Start: ' + '{0:%d.%m.%Y %H:%M:%S}'.format(self.analysis.time_min) + '\n'\
                    'End: ' + '{0:%d.%m.%Y %H:%M:%S}'.format(self.analysis.time_max) + '\n'
        except ValueError:
            dates = 'Start: ' + str(self.analysis.time_min) + '"\n'\
                    'End: ' + str(self.analysis.time_max) + '"\n'
        if self.analysis.time_step is not None:
            temporal_step = str(self.analysis.time_step) + ' seconds\n'
        else:
            temporal_step = 'N/A (pure spatial interpolation)\n'
        return 'File ' + input_for_notification + ' was successfully interpolated ' + 'and saved under :\n' + \
            self.output_file + '\n\nNumber of non-duplicate observations: ' + str(len(self.reader.points)) + '\n' \
            'Latitude: from ' + str(self.analysis.lat_min) + ' to ' + str(self.analysis.lat_max) + '\n' \
            'Longitude: from ' + str(self.analysis.lon_min) + ' to ' + str(self.analysis.lon_max) + '\n' \
            'Altitude: from ' + str(self.analysis.alt_min) + ' to ' + str(self.analysis.alt_max) + '\n' + dates + \
            'Temporal step: ' + temporal_step +\
            'Spatial density: ' + (str(self.analysis.density) + ' x ')*2 + str(self.analysis.density) + '\n' \
            'Phenomenon: ' + str(self.analysis.phenomenon) + '\n' \
            'Input values: from ' + str(self.analysis.input_min) + ' to ' + str(self.analysis.input_max) + '\n'\
            'Interpolated values: from ' + str(self.analysis.value_min) + ' to ' + str(self.analysis.value_max) + '\n'

    def interpolate(self):
        self.config(cursor='wait')
        self.update()
        nearest_neighbors = 6  # default
        power = 2  # default
        function = self.interpolation_methods_combo.get()

        # get nearest neighbors input
        try:
            nearest_neighbors = int(self.neighbors_spinner.get().strip())
            if nearest_neighbors > 50:
                nearest_neighbors = 50  # to maximum
                self.neighbors_edited = True
        except ValueError:
            nearest_neighbors = 6  # to default
            self.neighbors_edited = True
        # get power input
        try:
            power = int(self.power_spinner.get())
            if power > 3:
                power = 3  # to max
                self.power_edited = True
        except ValueError:
            power = 2  # to default
            self.power_edited = True

        # prepare parameters for RBF interpolation
        function_type = self.functions_combo.get()
        if 'Thin' in function_type:
            function_type = 'thin_plate'
        if 'Cub' in function_type:
            function_type = 'cubic'
        if 'Lin' in function_type:
            function_type = 'linear'

        lat_column = self.lat_combo.get()
        lon_column = self.lon_combo.get()
        alt_column = self.alt_combo.get()
        value_column = self.value_combo.get()
        timestamp_column = self.time_combo.get()

        lat_index = 2
        lon_index = 3
        alt_index = 4
        value_index = 13
        timestamp_index = 1

        for i in range(len(self.header)):
            if lat_column in self.header[i]:
                lat_index = i
                break
        for i in range(len(self.header)):
            if lon_column in self.header[i]:
                lon_index = i
                break
        for i in range(len(self.header)):
            if alt_column in self.header[i]:
                alt_index = i
                break
        for i in range(len(self.header)):
            if value_column in self.header[i]:
                value_index = i
                break
        for i in range(len(self.header)):
            if timestamp_column in self.header[i]:
                timestamp_index = i
                break

        try:
            spatial_density = int(self.density_spinner.get())
            if spatial_density > 50:
                spatial_density = 50
                self.density_edited = True
        except ValueError:
            spatial_density = 10  # default
            self.density_edited = True

        if 'Spatio' in function:  # spatio-temporal interpolation
            try:
                temporal_step = int(self.temporal_step_spinner.get())
                if temporal_step > self.max_temporal_step:
                    temporal_step = self.max_temporal_step  # if the input bigger than possible maximum
                    self.temporal_step_edited = True
            except ValueError:
                temporal_step = self.max_temporal_step  # to illustrate change, it has to be at least 2 cubes
                self.temporal_step_edited = True
            try:
                self.timescale = float(self.timescale_spinner.get())
            except ValueError:
                self.timescale = 1
                self.timescale_edited = True
            self.analysis = Analysis(temporal_step, spatial_density)
            self.analysis.nearest_neighbors = nearest_neighbors
            self.analysis.power = power
            self.analysis.function = function_type
            self.reader = reader = Reader(self.input_path)
            reader(lat_index, lon_index, alt_index, value_index, timestamp_index, self.analysis)
            if len(reader.times) > 0:
                times = reader.times
            else:
                times = reader.system_times
            if 'IDW' in function:
                self.analysis.interpolation_method = 'idw'
                interpolate_with_idw(analysis=self.analysis, points=reader.points, values=reader.values,
                                     filename=self.output_file, times=times, timescale=self.timescale)
            else:  # RBF
                self.analysis.interpolation_method = 'rbf'
                interpolate_with_rbf(analysis=self.analysis, points=reader.points, values=reader.values,
                                     filename=self.output_file, times=times, timescale=self.timescale)
        else:  # pure spatial interpolation
            self.analysis = Analysis(None, spatial_density)
            self.analysis.nearest_neighbors = nearest_neighbors
            self.analysis.power = power
            self.analysis.function = function_type
            self.reader = reader = Reader(self.input_path)
            reader(lat_index, lon_index, alt_index, value_index, timestamp_index, self.analysis)
            if 'IDW' in function:
                self.analysis.interpolation_method = 'idw'
                interpolate_with_idw(analysis=self.analysis, points=reader.points, values=reader.values,
                                     filename=self.output_file)
            else:
                self.analysis.interpolation_method = 'rbf'
                interpolate_with_rbf(analysis=self.analysis, points=reader.points, values=reader.values,
                                     filename=self.output_file)
        self.config(cursor='')

    def inform_parameters_set_to_default(self):
        info_to_default = ''
        if self.neighbors_edited or self.power_edited or self.density_edited or self.temporal_step_edited \
                or self.timescale_edited:
            info_to_default = 'One or more parameters set to default due to illegal input values:\n'
            if self.neighbors_edited:
                info_to_default += 'Number of nearest neighbors: ' + str(self.analysis.nearest_neighbors) + '\n'
            if self.power_edited:
                info_to_default += 'Power: ' + str(self.analysis.power) + '\n'
            if self.density_edited:
                info_to_default += 'Spatial density: ' + str(self.analysis.density) + '\n'
            if self.temporal_step_edited:
                info_to_default += 'Temporal step: ' + str(self.analysis.time_step) + '\n'
            if self.timescale_edited:
                info_to_default += 'Timescale: 1'
        return info_to_default

    def all_edited_parameter_flag_to_false(self):
        self.neighbors_edited = False
        self.power_edited = False
        self.density_edited = False
        self.temporal_step_edited = False
        self.timescale_edited = False

    @staticmethod
    def extract_filename(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def info(self):
        messagebox.showinfo(title='About the tool', message=info())


def start():
    root = Tk()
    root.title("Spatio-Temporal Interpolation")
    root.iconbitmap('icon.ico')
    content = Gui()
    content.pack()
    root.mainloop()
if __name__ == '__main__':
    start()
