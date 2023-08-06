from ml.ml40.features.properties.values.value import Value


class MaintenanceData(Value):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__lastMaintainOperatingHours = None
        self.__intervalTime = None
        self.__json_out = {}

    @property
    def lastMaintainOperatingHours(self):
        return self.__lastMaintainOperatingHours

    @lastMaintainOperatingHours.setter
    def lastMaintainOperatingHours(self, value):
        self.__lastMaintainOperatingHours = value

    @property
    def intervalTime(self):
        return self.__intervalTime

    @intervalTime.setter
    def intervalTime(self, value):
        self.__intervalTime = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.__lastMaintainOperatingHours is not None:
            self.__json_out["lastMaintainOperatingHours"] = self.__lastMaintainOperatingHours
        if self.__intervalTime is not None:
            self.__json_out["intervalTime"] = self.__intervalTime
        return self.__json_out
