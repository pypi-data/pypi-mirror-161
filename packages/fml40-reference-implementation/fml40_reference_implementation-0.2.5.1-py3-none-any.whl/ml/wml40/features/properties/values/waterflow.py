from ml.ml40.features.properties.values.value import Value


class WaterFlow(Value):
    def __init__(self, namespace="wml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__latestTime = None
        self.__latestValue = None
        self.__json_out = {}

    @property
    def latestTime(self):
        return self.__latestTime

    @latestTime.setter
    def latestTime(self, value):
        self.__latestTime = value

    @property
    def latestValue(self):
        return self.__latestValue

    @latestValue.setter
    def latestValue(self, value):
        self.__latestValue = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.latestTime is not None:
            self.__json_out["latestTime"] = self.latestTime
        if self.latestValue is not None:
            self.__json_out["latestValue"] = self.latestValue
        return self.__json_out
