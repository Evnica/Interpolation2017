# Class Analysis contains data on current data set: minimum and maximum of latitude / longitude / altitude  and
# analyzed value, as well as analysis parameters (analyzed phenomenon, time step and spatial density of the
# interpolated grid).

from decimal import *
import numpy


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
        self.value_max = None
        self.value_min = None
        self.phenomenon = 'Unknown'  # default
        self.phenomenon_unit = "Unknown"
        self.coos = 'WGS84'
        self.coos_unit = 'Decimal Degree (lat, lon), Meter (alt)'
        self.coords_order = '[lat, lon, alt]'

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

    def generate_grid(self):
        step = 1 / self.density
        getcontext().prec = 8
        grid = []
        for i in range(self.density):
            for j in range(self.density):
                for k in range(self.density):
                    grid.append([k * step + step / 2, j * step + step / 2, i * step + step / 2])
        return grid

    