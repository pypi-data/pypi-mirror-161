from ml.ml40.features.functionalities.functionality import Functionality
from ml.ml40.features.properties.values.moisture import Moisture
from ml.ml40.features.properties.values.temperature import Temperature


class ProvidesSoilData(Functionality):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name: Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def getLatestMoisture(self) -> Moisture:
        pass

    def getMoistureDataSeries(self, startTime, endTime) -> [Moisture]:
        pass
        
    def getLatestTemperature(self) -> Temperature:
        pass

    def getTemperatureDataSeries(self, startTime, endTime) -> [Temperature]:
        pass
