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