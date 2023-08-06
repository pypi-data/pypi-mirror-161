from ml.ml40.features.properties.values.value import Value


class WeatherData(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__latestTime = None
        self.__latestClouds = None
        self.__latestDetailedStatus = None
        self.__latestHumidity = None
        self.__latestRain = None
        self.__latestStatus = None
        self.__latestTemperature = None
        self.__json_out = {}

    @property
    def latestTime(self):
        return self.__latestTime

    @latestTime.setter
    def latestTime(self, value):
        self.__latestTime = value

    @property
    def latestClouds(self):
        return self.__latestClouds

    @latestClouds.setter
    def latestClouds(self, value):
        self.__latestClouds = value

    @property
    def latestDetailedStatus(self):
        return self.__latestDetailedStatus

    @latestDetailedStatus.setter
    def latestDetailedStatus(self, value):
        self.__latestDetailedStatus = value
        
    @property
    def latestHumidity(self):
        return self.__latestHumidity

    @latestHumidity.setter
    def latestHumidity(self, value):
        self.__latestHumidity = value
        
    @property
    def latestRain(self):
        return self.__latestRain

    @latestRain.setter
    def latestRain(self, value):
        self.__latestRain = value
        
    @property
    def latestStatus(self):
        return self.__latestStatus

    @latestStatus.setter
    def latestStatus(self, value):
        self.__latestStatus = value
        
    @property
    def latestTemperature(self):
        return self.__latestTemperature

    @latestTemperature.setter
    def latestTemperature(self, value):
        self.__latestTemperature = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.latestTime is not None:
            self.__json_out["latestTime"] = self.latestTime
        if self.latestClouds is not None:
            self.__json_out["latestClouds"] = self.latestClouds        
        if self.latestDetailedStatus is not None:
            self.__json_out["latestDetailedStatus"] = self.latestDetailedStatus        
        if self.latestHumidity is not None:
            self.__json_out["latestHumidity"] = self.latestHumidity        
        if self.latestRain is not None:
            self.__json_out["latestRain"] = self.latestRain        
        if self.latestStatus is not None:
            self.__json_out["latestStatus"] = self.latestStatus        
        if self.latestTemperature is not None:
            self.__json_out["latestTemperature"] = self.latestTemperature
        return self.__json_out