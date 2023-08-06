from ml.ml40.features.properties.values.value import Value


class WaterQuality(Value):
    def __init__(self, namespace="wml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__latestInorgN = None
        self.__latestNH4N = None
        self.__latestNO2N = None
        self.__latestNO3N = None
        self.__latestPHValue = None
        self.__latestTime = None
        self.__latestTOC = None
        self.__latestTP = None
        self.__json_out = {}

    @property
    def latestInorgN(self):
        return self.__latestInorgN

    @latestInorgN.setter
    def latestInorgN(self, value):
        self.__latestInorgN = value

    @property
    def latestNH4N(self):
        return self.__latestValue

    @latestNH4N.setter
    def latestNH4N(self, value):
        self.__latestValue = value

    @property
    def latestNO2N(self):
        return self.__latestNO2

    @latestNO2N.setter
    def latestNO2N(self, value):
        self.__latestNO2 = value
     
    @property
    def latestNO3N(self):
        return self.__latestNO3

    @latestNO3N.setter
    def latestNO3N(self, value):
        self.__latestNO3 = value

    @property
    def latestPHValue(self):
        return self.__latestPHValue

    @latestPHValue.setter
    def latestPHValue(self, value):
        self.__latestPHValue = value
        
    @property
    def latestTime(self):
        return self.__latestTime

    @latestTime.setter
    def latestTime(self, value):
        self.__latestTime = value
        
    @property
    def latestTOC(self):
        return self.__latestTOC

    @latestTOC.setter
    def latestTOC(self, value):
        self.__latestTOC = value
        
    @property
    def latestTP(self):
        return self.__latestTP

    @latestTP.setter
    def latestTP(self, value):
        self.__latestTP = value
        
    def to_json(self):
        self.__json_out = super().to_json()
        if self.latestInorgN is not None:
            self.__json_out["latestInorgN"] = self.latestInorgN
        if self.latestNH4N is not None:
            self.__json_out["latestNH4N"] = self.latestNH4N
        if self.latestNO2N is not None:
            self.__json_out["latestNO2N"] = self.latestNO2N        
        if self.latestNO3N is not None:
            self.__json_out["latestNO3N"] = self.latestNO3N        
        if self.latestPHValue is not None:
            self.__json_out["latestPHValue"] = self.latestPHValue        
        if self.latestTime is not None:
            self.__json_out["latestTime"] = self.latestTime        
        if self.latestTOC is not None:
            self.__json_out["latestTOC"] = self.latestTOC        
        if self.latestTP is not None:
            self.__json_out["latestTP"] = self.latestTP
        return self.__json_out
