from interpolation.analysis import Analysis
from interpolation.csvconverter import CsvConverter
from interpolation.iohelper import Writer


converter = CsvConverter('input/wetter.csv')
# def __call__(self, time_index, lat_index, lon_index, alt_index, temp_index, hum_index, press_index):
converter(1, 2, 3, 4, 13, 15, 14)
writer = Writer('output/initial_temp.json')
# initial_to_json_1phenomena(self, csv_converter, value_index):
writer.initial_to_json_1phenomena(converter, 0)
writer.set_output_name('output/initial_all.json')
writer.initial_to_json(converter)


