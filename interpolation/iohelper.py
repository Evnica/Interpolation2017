from dateutil import parser


class Reader:
    def __init__(self, file_name):
        self.file_name = file_name
        self.analysis = None

    def get_column_names(self):
        file = open(self.file_name)
        header = []
        for line in file:
            if 'lat' in line:
                header = line.split(';')
                break
        file.close()
        return header

    def __call__(self, lat_index, lon_index, alt_index, value_index, time_index, analysis):

        header = self.get_column_names()
        if 'temp' in header[value_index]:
            analysis.set_phenomenon(0)  # temperature
        elif 'hum' in header[value_index]:
            analysis.set_phenomenon(2)  # humidity
        elif 'press' in header[value_index]:
            analysis.set_phenomenon(1)  # pressure
        else:
            analysis.set_phenomenon(-1)  # unknown

        file = open(self.file_name)
        i = 0
        j = 0
        times = []  # 2016-07-28T08:17:33,082Z
        values = []
        lat_values = []
        lon_values = []
        alt_values = []

        for line in file:
            i += 1
            line_content = line.split(';')
            if len(line_content) >= (max([lat_index, lon_index, alt_index, value_index, time_index]) + 1):
                try:
                    if not line_content[lat_index] == '0' and not line_content[lat_index] == 'nan' and not line_content[
                        lon_index] == '0' and not line_content[lon_index] == 'nan' and not line_content[
                        alt_index] == '0' and not line_content[alt_index] == 'nan' and not line_content[
                                                                                  value_index] == 'nan':
                        current_lat = float(line_content[lat_index].replace(",", "."))
                        current_lon = float(line_content[lon_index].replace(",", "."))
                        current_alt = float(line_content[alt_index].replace(",", "."))
                        current_value = float(line_content[value_index].replace(",", "."))
                        lat_values.append(current_lat)
                        lon_values.append(current_lon)
                        alt_values.append(current_alt)
                        values.append(current_value)
                        times.append(parser.parse(line_content[time_index]))
                except ValueError:
                    j += 1
                    "Not all necessary values present in line " + str(i)
        file.close()
        lat_max = max(lat_values)
        lat_min = min(lat_values)
        lon_max = max(lon_values)
        lon_min = min(lon_values)
        alt_max = max(alt_values)
        alt_min = min(alt_values)

        analysis.set_lat_limits(lat_max, lat_min)
        analysis.set_lon_limits(lon_max, lon_min)
        analysis.set_alt_limits(alt_max, alt_min)
        analysis.value_max = max(values)
        analysis.value_min = min(values)

        lat_values = [(lat - lat_min) / (lat_max - lat_min) for lat in lat_values]
        lon_values = [(lon - lon_min) / (lon_max - lon_min) for lon in lon_values]
        alt_values = [(alt - alt_min) / (alt_max - alt_min) for alt in alt_values]

        points = list(map(list, zip(lat_values, lon_values, alt_values)))
        self.points = points
        self.values = values
        self.times = times
        self.analysis = analysis
        return points, values, times
