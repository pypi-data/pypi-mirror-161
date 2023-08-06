from ml.ml40.features.properties.values.value import Value


class Temperature(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__temperature = None
        self.__latestTime = None
        self.__json_out = dict()

    @property
    def temperature(self):
        return self.__temperature

    @temperature.setter
    def temperature(self, value):
        if isinstance(value, (float, int)):
            self.__temperature = value
        else:
            raise TypeError
            
    @property
    def latestTime(self):
        return self.__latestTime

    @latestTime.setter
    def latestTime(self, value):
        self.__latestTime = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.temperature is not None:
            self.__json_out["temperature"] = self.temperature
        if self.latestTime is not None:
            self.__json_out["latestTime"] = self.latestTime
        return self.__json_out
