from ml.ml40.features.properties.values.value import Value


class Moisture(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__humidity = None
        self.__latestTime = None 
        self.__json_out = dict()

    @property
    def humidity(self):
        return self.__humidity

    @humidity.setter
    def humidity(self, value):
        self.__humidity = value

    @property
    def latestTime(self):
        return self.__latestTime

    @latestTime.setter
    def latestTime(self, value):
        self.__latestTime = value
        
    def to_json(self):
        self.__json_out = super().to_json()
        if self.humidity is not None:
            self.__json_out["humidity"] = self.humidity
        if self.latestTime is not None:
            self.__json_out["latestTime"] = self.latestTime
        return self.__json_out
