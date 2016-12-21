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


class Writer:

    def __init__(self, output_name):
        self.output_name = output_name

    def set_output_name(self, output_name):
        self.output_name = output_name

    # write a grid dataset to json
    def write_spatial_grid_to_json(self, grid, values, analysis, times):
        output = open(self.output_name, 'w')
        output.write('[\n')
        output.write('{"Metadata":')
        output.write('{\n"time_step":"' + str(analysis.time_step) + '",\n'
                     '"density":"' + str(analysis.density) + '",\n'
                     '"phenomenon":"' + analysis.phenomenon + '",\n'
                     '"units":"' + analysis.phenomenon_unit + '",\n'
                     '"coordinate system":"' + analysis.coos + '",\n'
                     '"coordinate system unit":"' + analysis.coos_unit + '",\n'
                     '"coordinate order":"' + analysis.coords_order + '",\n'
                     '"lat_max":"' + str(analysis.lat_max) + '",\n'
                     '"lat_min":"' + str(analysis.lat_min) + '",\n'
                     '"lon_max":"' + str(analysis.lon_max) + '",\n'
                     '"lon_min":"' + str(analysis.lon_min) + '",\n'
                     '"alt_max":"' + str(analysis.alt_max) + '",\n'
                     '"alt_min":"' + str(analysis.alt_min) + '",\n'
                     )
        if times[0] is not None and times[1] is not None:
            output.write('"time_max":"' + '{0:%d.%m.%Y %H:%M:%S}'.format(times[-1]) + '",\n'
                         '"time_min":"' + '{0:%d.%m.%Y %H:%M:%S}'.format(times[0]) + '",\n'
                         '"value_max":"' + str(max(values)) + '",\n'
                         '"value_min":"' + str(min(values)) + '"\n'
                         '}},'
                         '\n'
                         '{"0":[\n')
        else:
            output.write('"time_max":"None",\n'
                         '"time_min":"None",\n'
                         '"value_max":"' + str(max(values)) + '",\n'
                         '"value_min":"' + str(min(values)) + '"\n'
                         '}},'
                         '\n'
                         '{"0":[\n')
        for i in range(len(grid) - 1):
            output.write('{"coords":[' + format(grid[i][0], '.3f') + ', ' + format(grid[i][1], '.3f') + ', ' +
                         format(grid[i][2], '.3f') + ']' + ','
                         ' "val":"' + str(values[i]) + '"},\n')
        output.write('{"coords":[' + format(grid[-1][0], '.3f') + ', ' + format(grid[-1][1], '.3f') + ', ' +
                     format(grid[-1][2], '.3f') + ']' + ', "val":"' + str(values[-1]) + '"}]\n')
        output.write("}\n]")
        output.close()

    def write_initial_to_json(self, analysis, times, points, values):
        output = open(self.output_name, 'w')
        output.write('[')
        output.write('{\n'
                     '"lat_max":"' + str(analysis.lat_max) + '",\n'
                     '"lat_min":"' + str(analysis.lat_min) + '",\n'
                     '"lon_max":"' + str(analysis.lon_max) + '",\n'
                     '"lon_min":"' + str(analysis.lon_min) + '",\n'
                     '"alt_max":"' + str(analysis.alt_max) + '",\n'
                     '"alt_min":"' + str(analysis.alt_min) + '",\n'
                     '"time_max":"' + str(times[-1]) + '",\n'
                     '"time_min":"' + str(times[0]) + '",\n'
                     '"value_max":"' + str(analysis.value_max) + '",\n'
                     '"value_min":"' + str(analysis.value_min) + '"\n'
                     '},'
                     '\n'
                     '{\n"0":[')
        for i in range(len(values) - 2):
            output.write('{"coords":' + str(points[i]) + ','
                         ' "val":"' + str(values[i]) + '"},\n')
        output.write('{"coordinates":' + str(points[-1]) + ', "value":"' + str(values[-1]) + '"}]\n')
        output.write("}\n]")
        output.close()

    # write one of the phenomena of the initial csv to json without analysis
    def initial_to_json_1phenomena(self, csv_converter, value_index):

        coos = 'WGS84'
        coos_unit = 'Decimal Degree (lat, lon), Meter (alt)'
        coords_order = '[lat, lon, alt]'
        if value_index == 0:  # temperature
            values = csv_converter.temp_values
            value_max = csv_converter.temp_max
            value_min = csv_converter.temp_min
            phenomenon = 'Temperature'
            phenomenon_unit = 'Degree Celsius'
        elif value_index == 1:  # pressure
            values = csv_converter.press_values
            value_max = csv_converter.press_max
            value_min = csv_converter.press_min
            phenomenon = 'Pressure'
            phenomenon_unit = 'mmHg'
        else:  # default:humidity
            values = csv_converter.hum_values
            value_max = csv_converter.hum_max
            value_min = csv_converter.hum_min
            phenomenon = 'Humidity'
            phenomenon_unit = '%'

        output = open(self.output_name, 'w')
        output.write('[')
        output.write('{"Metadata":\n')
        output.write('{\n'
                     '"phenomenon":"' + phenomenon + '",\n'
                     '"units":"' + phenomenon_unit + '",\n'
                     '"coordinate system":"' + coos + '",\n'
                     '"coordinate system unit":"' + coos_unit + '",\n'
                     '"coordinate order":"' + coords_order + '",\n'
                     '"lat_max":"' + str(csv_converter.lat_max) + '",\n'
                     '"lat_min":"' + str(csv_converter.lat_min) + '",\n'
                     '"lon_max":"' + str(csv_converter.lon_max) + '",\n'
                     '"lon_min":"' + str(csv_converter.lon_min) + '",\n'
                     '"alt_max":"' + str(csv_converter.alt_max) + '",\n'
                     '"alt_min":"' + str(csv_converter.alt_min) + '",\n'
                     '"time_max":"' + str(csv_converter.times[-1]) + '",\n'
                     '"time_min":"' + str(csv_converter.times[0]) + '",\n'
                     '"value_max":"' + str(value_max) + '",\n'
                     '"value_min":"' + str(value_min) + '"\n'
                     '}},'
                     '\n'
                     '{\n"0":[')
        for i in range(len(csv_converter.lat_values) - 1):
            output.write('{"coords":[' + str(csv_converter.lat_values[i]) + ', '
                         + str(csv_converter.lon_values[i]) + ', '
                         + str(csv_converter.alt_values[i]) + '], "val":"' + str(values[i]) + '"},\n')
        output.write('{"coordinates":[' + str(csv_converter.lat_values[-1]) + ', ' +
                     str(csv_converter.lon_values[-1]) + ', ' + str(csv_converter.alt_values[-1]) +
                     '], "value":"' + str(values[-1]) + '"}]\n')
        output.write("}\n]")
        output.close()

    # write complete initial csv to json without analysis
    def initial_to_json(self, csv_converter):
        coos = 'WGS84'
        coos_unit = 'Decimal Degree (lat, lon), Meter (alt)'
        coords_order = '[lat, lon, alt]'
        output = open(self.output_name, 'w')
        output.write('[')
        output.write('{"Metadata":\n')
        output.write('{\n'
                     '"phenomena":"Temperature(Degree Celsius), Pressure(mmHg), Humidity(%)' + '",\n'
                     '"phenomena order":"Temperature, Pressure, Humidity",\n'
                     '"coordinate system":"' + coos + '",\n'
                     '"coordinate system unit":"' + coos_unit + '",\n'
                     '"coordinate order":"' + coords_order + '",\n'
                     '"lat_max":"' + str(csv_converter.lat_max) + '",\n'
                     '"lat_min":"' + str(csv_converter.lat_min) + '",\n'
                     '"lon_max":"' + str(csv_converter.lon_max) + '",\n'
                     '"lon_min":"' + str(csv_converter.lon_min) + '",\n'
                     '"alt_max":"' + str(csv_converter.alt_max) + '",\n'
                     '"alt_min":"' + str(csv_converter.alt_min) + '",\n'
                     '"time_max":"' + '{0:%d.%m.%Y %H:%M:%S}'.format(csv_converter.times[-1]) + '",\n'
                     '"time_min":"' + '{0:%d.%m.%Y %H:%M:%S}'.format(csv_converter.times[0]) + '",\n'
                     '"temp_max":"' + str(csv_converter.temp_max) + '",\n'
                     '"temp_min":"' + str(csv_converter.temp_min) + '",\n'
                     '"hum_max":"' + str(csv_converter.hum_max) + '",\n'
                     '"hum_min":"' + str(csv_converter.hum_min) + '",\n'
                     '"press_max":"' + str(csv_converter.press_max) + '",\n'
                     '"press_min":"' + str(csv_converter.press_min) + '"\n'
                     '}},'
                     '\n'
                     '{\n"0":[')
        for i in range(len(csv_converter.lat_values) - 1):
            output.write('{"coords":[' + str(csv_converter.lat_values[i]) + ', '
                         + str(csv_converter.lon_values[i]) + ', '
                         + str(csv_converter.alt_values[i]) + '], "val":[' + str(csv_converter.temp_values[i]) + ', '
                         + str(csv_converter.press_values[i]) + ', '
                         + str(csv_converter.hum_values[i]) + ']},\n')
        output.write('{"coords":[' + str(csv_converter.lat_values[-1]) + ', ' +
                     str(csv_converter.lon_values[-1]) + ', ' + str(csv_converter.alt_values[-1]) +
                     '], "val":[' + str(csv_converter.temp_values[-1]) + ', '
                     + str(csv_converter.press_values[-1]) + ', '
                     + str(csv_converter.hum_values[-1]) + ']}\n')
        output.write("]}\n]")
        output.close()

        # write statistical quality analysis results to csv
        def write_quality_test_to_csv(self, mae, mse, rmse, mare, r2, num_of_known, num_of_query):
            self.output_name += '.csv'
            csv_output = open(self.output_name, 'w')
            csv_output.write('iteration;num_known;num_query;MAE;MSE;RMSE;MARE;R^2\n')
            for index in range(len(mae)):
                csv_output.write(str(index) + ';' + str(num_of_known[index]) + ';' + str(num_of_query[index]) + ';' +
                                 str(mae[index]) + ';' + str(mse[index]) + ';' + str(rmse[index]) + ';' +
                                 str(mare[index]) + ';' + str(r2[index]) + '\n')
            csv_output.close()
