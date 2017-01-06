from dateutil import parser
import statistics
import random


class Reader:
    def __init__(self, file_name):
        self.file_name = file_name
        self.analysis = None
        self.times = []  # 2016-07-28T08:17:33,082Z
        self.system_times = []
        self.values = []
        self.points = []

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
        analysis.header = header
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
        lat_values = []
        lon_values = []
        alt_values = []

        potential_duplicate_lat = -1
        potential_duplicate_lon = -1
        potential_duplicate_alt = -1

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

                        if potential_duplicate_lat != current_lat or \
                           potential_duplicate_lon != current_lon or potential_duplicate_alt != current_alt:
                            random_noise = random.uniform(0.0000000001, 0.000000009)
                            if potential_duplicate_lat != current_lat:
                                lat_values.append(current_lat)
                            else:
                                lat_values.append(current_lat + random_noise)
                            if potential_duplicate_lon != current_lon:
                                lon_values.append(current_lon)
                            else:
                                lon_values.append(current_lon + random_noise)
                            if potential_duplicate_alt != current_alt:
                                alt_values.append(current_alt)
                            else:
                                alt_values.append(current_alt + random_noise)

                            self.values.append(current_value)

                            potential_duplicate_lat = current_lat
                            potential_duplicate_lon = current_lon
                            potential_duplicate_alt = current_alt

                            try:
                                self.times.append(parser.parse(line_content[time_index]))
                            except ValueError:
                                self.system_times.append(line_content[time_index])
                except ValueError:
                    j += 1
                    # print("Not all necessary values are present in the line " + str(i))
        # print(str(j) + ' lines were not valid')
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
        analysis.input_max = max(self.values)
        analysis.input_min = min(self.values)

        lat_values = [(lat - lat_min) / (lat_max - lat_min) for lat in lat_values]
        lon_values = [(lon - lon_min) / (lon_max - lon_min) for lon in lon_values]
        alt_values = [(alt - alt_min) / (alt_max - alt_min) for alt in alt_values]
        self.points = list(map(list, zip(lat_values, lon_values, alt_values)))

        time_max = time_min = None
        if len(self.times) > 0:
            times = [dt.replace(tzinfo=None) for dt in self.times]
            self.times = times
            time_max = max(self.times)
            time_min = min(self.times)
        elif len(self.system_times) > 0:
            time_max = max(self.system_times)
            time_min = min(self.system_times)
        analysis.set_times(time_max, time_min)

        self.analysis = analysis

        if len(self.times) > 0:
            return self.points, self.values, self.times
        else:
            return self.points, self.values, self.system_times


class Writer:

    def __init__(self, output_name):
        self.output_name = output_name
        self.coos = 'WGS84'
        self.coos_unit = 'Decimal Degree (lat, lon), Meter (alt)'
        self.coords_order = '[lat, lon, alt]'

    def set_output_name(self, output_name):
        self.output_name = output_name

    # write a grid dataset to json
    def write_spatial_grid_to_json(self, grid, values, analysis):
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
        if analysis.time_max is not None and analysis.time_min is not None:
            try:
                output.write('"time_max":"' + '{0:%d.%m.%Y %H:%M:%S}'.format(analysis.time_max) + '",\n'
                             '"time_min":"' + '{0:%d.%m.%Y %H:%M:%S}'.format(analysis.time_min) + '",\n')
            except ValueError:
                output.write('"time_max":"' + str(analysis.time_max) + '",\n'
                             '"time_min":"' + str(analysis.time_min) + '",\n')

        else:
            output.write('"time_max":"None",\n'
                         '"time_min":"None",\n')
        output.write('"value_max":"' + str(max(values)) + '",\n'
                     '"value_min":"' + str(min(values)) + '"\n}},\n'
                     '{"0":[\n')
        for i in range(len(grid) - 1):
            output.write('{"coords":[' + format(grid[i][0], '.3f') + ', ' + format(grid[i][1], '.3f') + ', ' +
                         format(grid[i][2], '.3f') + ']' + ','
                         ' "val":"' + str(values[i]) + '"},\n')
        output.write('{"coords":[' + format(grid[-1][0], '.3f') + ', ' + format(grid[-1][1], '.3f') + ', ' +
                     format(grid[-1][2], '.3f') + ']' + ', "val":"' + str(values[-1]) + '"}]\n')
        output.write("}\n]")
        output.close()

    def write_time_series_grids_to_json(self, grids, grid_values, analysis):
        output = open(self.output_name, 'w')
        # our json contains an array of objects
        output.write('[\n')
        # the first object is metadata with one key "Metadata"
        output.write('{"Metadata":')
        # its value is an object of dataset properties
        output.write('{\n'
                     '"time_step":"' + str(analysis.time_step) + '",\n'
                     '"density":"' + str(analysis.density) + '",\n'
                     '"phenomenon":"' + analysis.phenomenon + '",\n'
                     '"units":"' + analysis.phenomenon_unit + '",\n'
                     '"coordinate system":"' + self.coos + '",\n'
                     '"coordinate system unit":"' + self.coos_unit + '",\n'
                     '"coordinate order":"' + self.coords_order + '",\n'
                     '"lat_max":"' + str(analysis.lat_max) + '",\n'
                     '"lat_min":"' + str(analysis.lat_min) + '",\n'
                     '"lon_max":"' + str(analysis.lon_max) + '",\n'
                     '"lon_min":"' + str(analysis.lon_min) + '",\n'
                     '"alt_max":"' + str(analysis.alt_max) + '",\n'
                     '"alt_min":"' + str(analysis.alt_min) + '",\n')
        try:
            output.write('"time_max":"' + '{0:%d.%m.%Y %H:%M:%S}'.format(analysis.time_max) + '",\n'
                         '"time_min":"' + '{0:%d.%m.%Y %H:%M:%S}'.format(analysis.time_min) + '",\n')
        except ValueError:
            output.write('"time_max":"' + str(analysis.time_max) + '",\n'
                         '"time_min":"' + str(analysis.time_min) + '",\n')
        output.write('"input_max":"' + str(analysis.input_max) + '",\n'
                     '"input_min":"' + str(analysis.input_min) + '",\n'
                     '"value_max":"' + str(analysis.value_max) + '",\n'
                     '"value_min":"' + str(analysis.value_min) + '",\n'
                     '"within_range":"' + str(analysis.interpolated_within_range) + '"\n}},\n')  # close metadata object
        if len(grids) > 1:
            # for all grids but the last
            for j in range(len(grids) - 1):
                # create a grid object with the key corresponding to the index of the grid
                # its value is an array of objects, each of which contains 2 key-value pairs: coordinates and values
                output.write('{"' + str(j) + '":[\n')
                # for all points in the grid but the last
                for i in range(len(grids[j]) - 1):
                    # write coords and values of each point to a grid object, ending it with a ','
                    output.write('{"coords":[' + format(grids[j][i][0], '.3f') + ', ' + format(grids[j][i][1], '.3f') +
                                 ', ' + format(grids[j][i][2], '.3f') + '], "val":' + str(grid_values[j][i]) + '},\n')
                # for the last point in the grid, write its coords and values and close the grid object
                output.write('{"coords":[' + format(grids[j][-1][0], '.3f') + ', ' + format(grids[j][-1][1], '.3f')
                             + ', ' + format(grids[j][-1][2], '.3f') + '], "val":' + str(grid_values[j][-1]) + '}\n')
                # close array of coords/values and the grid object; line ends with "," - one more grid expected
                output.write(']},\n')
        # open last (or only) grid object
        output.write('{"' + str(len(grids) - 1) + '":[\n')
        for i in range(0, len(grids[-1])):
            # write coords and values of each point to a grid object, ending it with a ','
            output.write('{"coords":[' + format(grids[-1][i][0], '.3f') + ', ' + format(grids[-1][i][1], '.3f') + ', '
                         + format(grids[-1][i][2], '.3f') + '], "val":' + str(grid_values[-1][i]) + '},\n')
        # for the last point in the grid, write its coords and values and close the grid object
        output.write('{"coords":[' + format(grids[-1][-1][0], '.3f') + ', ' + format(grids[-1][-1][1], '.3f') + ', '
                     + format(grids[-1][-1][2], '.3f') + '], "val":' + str(grid_values[-1][-1]) + '}\n')
        # close array of points and the last grid object
        output.write(']\n}')
        # close top level json array
        output.write("\n]")
        output.close()

    # write one of the phenomena of the initial csv to json without analysis
    # value_index 0 - temperature, 1 - pressure, any other - humidity
    def initial_to_json_1phenomena(self, csv_converter, value_index=2):

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
                     '"coordinate system":"' + self.coos + '",\n'
                     '"coordinate system unit":"' + self.coos_unit + '",\n'
                     '"coordinate order":"' + self.coords_order + '",\n'
                     '"lat_max":"' + str(csv_converter.lat_max) + '",\n'
                     '"lat_min":"' + str(csv_converter.lat_min) + '",\n'
                     '"lon_max":"' + str(csv_converter.lon_max) + '",\n'
                     '"lon_min":"' + str(csv_converter.lon_min) + '",\n'
                     '"alt_max":"' + str(csv_converter.alt_max) + '",\n'
                     '"alt_min":"' + str(csv_converter.alt_min) + '",\n')
        try:
            output.write('"time_max":"' + '{0:%d.%m.%Y %H:%M:%S}'.format(csv_converter.time_max) + '",\n'
                         '"time_min":"' + '{0:%d.%m.%Y %H:%M:%S}'.format(csv_converter.time_min) + '",\n')
        except ValueError:
            output.write('"time_max":"' + str(csv_converter.time_max) + '",\n'
                         '"time_min":"' + str(csv_converter.time_min) + '",\n')
        output.write('"value_max":"' + str(value_max) + '",\n'
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

        output = open(self.output_name, 'w')
        output.write('[')
        output.write('{"Metadata":\n')
        output.write('{\n'
                     '"phenomena":"Temperature(Degree Celsius), Pressure(mmHg), Humidity(%)' + '",\n'
                     '"phenomena order":"Temperature, Pressure, Humidity",\n'
                     '"coordinate system":"' + self.coos + '",\n'
                     '"coordinate system unit":"' + self.coos_unit + '",\n'
                     '"coordinate order":"' + self.coords_order + '",\n'
                     '"lat_max":"' + str(csv_converter.lat_max) + '",\n'
                     '"lat_min":"' + str(csv_converter.lat_min) + '",\n'
                     '"lon_max":"' + str(csv_converter.lon_max) + '",\n'
                     '"lon_min":"' + str(csv_converter.lon_min) + '",\n'
                     '"alt_max":"' + str(csv_converter.alt_max) + '",\n'
                     '"alt_min":"' + str(csv_converter.alt_min) + '",\n')
        try:
            output.write('"time_max":"' + '{0:%d.%m.%Y %H:%M:%S}'.format(csv_converter.time_max) + '",\n'
                         '"time_min":"' + '{0:%d.%m.%Y %H:%M:%S}'.format(csv_converter.time_min) + '",\n')
        except ValueError:
            output.write('"time_max":"' + str(csv_converter.time_max) + '",\n'
                         '"time_min":"' + str(csv_converter.time_min) + '",\n')
        output.write('"temp_max":"' + str(csv_converter.temp_max) + '",\n'
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

    # write statistical quality analysis results to csv
    def write_quality_test_to_csv(self, mae, mse, rmse, mare, r2, num_of_known, num_of_query):
        self.output_name += '.csv'
        output = open(self.output_name, 'w')
        output.write('iteration;num_known;num_query;MAE;MSE;RMSE;MARE;R^2\n')
        for i in range(len(mae)):
            output.write(str(i) + ';' + str(num_of_known[i]) + ';' + str(num_of_query[i]) + ';' + str(mae[i]) + ';' +
                         str(mse[i]) + ';' + str(rmse[i]) + ';' + str(mare[i]) + ';' + str(r2[i]) + '\n')
        output.close()

    def write_quality_with_avg_to_csv(self, mae, mse, rmse, mare, r2, num_of_known, num_of_query):
        self.output_name += '.csv'
        output = open(self.output_name, 'w')
        output.write('iteration;num_known;num_query;MAE;MSE;RMSE;MARE;R^2\n')
        for i in range(len(mae)):
            output.write(str(i) + ';' + str(num_of_known[i]) + ';' + str(num_of_query[i]) + ';' + str(mae[i]) + ';' +
                         str(mse[i]) + ';' + str(rmse[i]) + ';' + str(mare[i]) + ';' + str(r2[i]) + '\n')
        output.write('AVG;' + str(statistics.mean(num_of_known)) + ';' + str(statistics.mean(num_of_query)) + ';' +
                     str(statistics.mean(mae)) + ';' + str(statistics.mean(mse)) + ';' + str(statistics.mean(rmse)) +
                     ';' + str(statistics.mean(mare)) + ';' + str(statistics.mean(r2)))
        output.close()

    def write_quality_comparison(self, descriptions, mae, mse, rmse, mare, r2):
        self.output_name += '.csv'
        output = open(self.output_name, 'w')
        output.write('#;description;MAE;MSE;RMSE;MARE;R^2\n')
        for i in range(len(mae)):
            output.write(str(i) + ';' + descriptions[i] + ';' + str(mae[i]) + ';' + str(mse[i]) + ';' + str(rmse[i]) +
                         ';' + str(mare[i]) + ';' + str(r2[i]) + '\n')
        output.close()
