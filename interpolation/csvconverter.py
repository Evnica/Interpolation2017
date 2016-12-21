# CsvConverter converts all input data into format suitable for the json output of initial dataset


from dateutil import parser


class CsvConverter:
    def __init__(self, filename):
        self.filename = filename
        self.lat_max = None
        self.lat_min = None
        self.lon_max = None
        self.lon_min = None
        self.alt_max = None
        self.alt_min = None
        self.temp_max = None
        self.temp_min = None
        self.hum_max = None
        self.hum_min = None
        self.press_max = None
        self.press_min = None
        self.times = []
        self.lat_values = []
        self.lon_values = []
        self.alt_values = []
        self.temp_values = []
        self.hum_values = []
        self.press_values = []

    def __call__(self, time_index, lat_index, lon_index, alt_index, temp_index, hum_index, press_index):
        file = open(self.filename)
        j = 0

        for line in file:
            line_content = line.split(';')
            try:
                if not line_content[lat_index] == '0' and not line_content[lat_index] == 'nan' and not line_content[
                        lon_index] == '0' and not line_content[lon_index] == 'nan' and not line_content[
                        alt_index] == '0' and not line_content[alt_index] == 'nan' and not line_content[
                        temp_index] == 'nan' and not line_content[hum_index] == 'nan' \
                        and not line_content[press_index] == 'nan':
                    self.times.append(parser.parse(line_content[time_index]))
                    self.lat_values.append(float(line_content[lat_index].replace(",", ".")))
                    self.lon_values.append(float(line_content[lon_index].replace(",", ".")))
                    self.alt_values.append(float(line_content[alt_index].replace(",", ".")))
                    self.temp_values.append(float(line_content[temp_index].replace(",", ".")))
                    self.hum_values.append(float(line_content[hum_index].replace(",", ".")))
                    self.press_values.append(float(line_content[press_index].replace(",", ".")))
            except ValueError:
                j += 1
        file.close()
        self.lat_max = max(self.lat_values)
        self.lat_min = min(self.lat_values)
        self.lon_max = max(self.lon_values)
        self.lon_min = min(self.lon_values)
        self.alt_max = max(self.alt_values)
        self.alt_min = min(self.alt_values)
        self.temp_max = max(self.temp_values)
        self.temp_min = min(self.temp_values)
        self.hum_max = max(self.hum_values)
        self.hum_min = min(self.hum_values)
        self.press_max = max(self.press_values)
        self.press_min = min(self.press_values)
