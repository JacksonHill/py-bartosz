"""
Single reading instance.
It may be saved when is_complete
"""
class Reading(object):
    """
    Single reading instance.
    It may be saved when is_complete
    """

    def __init__(self, **kwargs):
        """
        Default init using kwargs
        """

        self.curr_time = kwargs.get('curr_time', None)
        self.curr_date = kwargs.get('curr_date', None)
        self.curr_flow = kwargs.get('curr_flow', None)
        self.program_until = kwargs.get('program_until', None)
        self.curr_mode = kwargs.get('curr_mode', None)

        self.inlet_temp = None
        self.outlet_temp = None
        self.external_temp = None

    def fill_fields(self, **kwargs):
        """
        Should be called after each reading from serial port
        """
        self.curr_time = kwargs.get('curr_time', None)
        self.curr_date = kwargs.get('curr_date', None)
        self.curr_flow = kwargs.get('curr_flow', None)
        self.program_until = kwargs.get('program_until', None)
        self.curr_mode = kwargs.get('curr_mode', None)
        self.set_temperature(displayed_temp=kwargs.get('displayed_temp', None))

    def set_temperature(self, displayed_temp=None):
        """
        Method for setting all 3 available temperatures
        """
        def normalize(temp):
            """
            strip celsius
            convert to float
            """
            temp = temp.split('$C')[0]
            temp = temp.replace(',', '.')
            try:
                return float(temp)
            except ValueError:
                return None

        if 'Temp. zew.' in displayed_temp:
            temp = displayed_temp.split('Temp. zew. ')[1].strip()
            self.external_temp = normalize(temp)

        if 'Temp. wyc.' in displayed_temp:
            temp = displayed_temp.split('Temp. wyc. ')[1].strip()
            self.outlet_temp = normalize(temp)

        if 'Temp. naw.' in displayed_temp:
            temp = displayed_temp.split('Temp. naw. ')[1].strip()
            self.inlet_temp = normalize(temp)

    def is_complete(self):
        """
        Reading is ready for further processing when all 3 temps are read.
        """
        return self.inlet_temp and self.outlet_temp and self.external_temp

    def save(self):
        """
        Save to time-series db
        """
        pass

    def clean(self):
        """
        Flush temperature data for next read
        """
        self.inlet_temp = None
        self.outlet_temp = None
        self.external_temp = None
