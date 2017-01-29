# Class Analysis contains data on current data set: minimum and maximum of latitude / longitude / altitude  and
# analyzed value, as well as analysis parameters (analyzed phenomenon, time step and spatial density of the
# interpolated grid).

from decimal import *
import interpolation.utils as utils


class Analysis:
    def __init__(self, time_step, density):
        self.time_step = time_step
        self.density = density
        self.lat_max = None
        self.lat_min = None
        self.lon_max = None
        self.lon_min = None
        self.alt_max = None
        self.alt_min = None
        self.input_max = None
        self.input_min = None
        self.value_max = None
        self.value_min = None
        self.time_min = None
        self.time_max = None
        self.phenomenon = 'Unknown'  # default
        self.phenomenon_unit = "Unknown"
        self.coos = 'WGS84'
        self.coos_unit = 'Decimal Degree (lat, lon), Meter (alt)'
        self.coords_order = '[lat, lon, alt]'
        self.header = None
        self.nearest_neighbors = 6
        self.power = 2
        self.function = 'thin_plate'
        self.interpolation_method = None
        self.dimension = None
        self.interpolated_total = None
        self.interpolated_within_range = None

    def set_phenomenon(self, phenomenon):
        if phenomenon == 0:
            self.phenomenon = 'Air Temperature'
            self.phenomenon_unit = "Degree Celsius"
        elif phenomenon == 1:
            self.phenomenon = 'Pressure'
            self.phenomenon_unit = "mmHg"
        elif phenomenon == 2:
            self.phenomenon = 'Humidity'
            self.phenomenon_unit = "%"
        else:
            self.phenomenon = 'Unknown'
            self.phenomenon_unit = "Unknown"

    def set_lat_limits(self, lat_max, lat_min):
        self.lat_max = lat_max
        self.lat_min = lat_min

    def set_lon_limits(self, lon_max, lon_min):
        self.lon_max = lon_max
        self.lon_min = lon_min

    def set_alt_limits(self, alt_max, alt_min):
        self.alt_max = alt_max
        self.alt_min = alt_min

    def set_times(self, time_max, time_min):
        self.time_max = time_max
        self.time_min = time_min

    def generate_grid(self):
        step = round(1 / self.density, 5)
        half_step = round(step / 2, 5)
        getcontext().prec = 8
        grid = []
        for i in range(self.density):
            for j in range(self.density):
                for k in range(self.density):
                    grid.append([round((k * step + half_step), 5), round((j * step + half_step), 5),
                                 round((i * step + half_step), 5)])
        return grid

    def generate_time_series_grids(self, timestamps):
        time_handler = utils.TimeHandler(timestamps)
        duration = time_handler.time_max - time_handler.time_min
        num_of_grids = int(duration // self.time_step) + 1
        grid = self.generate_grid()
        time_series_grids = []
        for i in range(0, num_of_grids):
            current_grid = []
            current_timestamp = time_handler.time_min + self.time_step*i
            if current_timestamp > time_handler.time_max:
                current_timestamp = time_handler.time_max
            normalized_time = time_handler.get_normalized_timestamp(current_timestamp)
            for j in range(0, len(grid)):
                current_grid.append([grid[j][0], grid[j][1], grid[j][2], normalized_time])
            time_series_grids.append(current_grid)
        if duration % self.time_step != 0 and num_of_grids > 1:
            current_grid = []
            for j in range(0, len(grid)):
                current_grid.append([grid[j][0], grid[j][1], grid[j][2], 1.0])
            time_series_grids.append(current_grid)
        return time_series_grids
