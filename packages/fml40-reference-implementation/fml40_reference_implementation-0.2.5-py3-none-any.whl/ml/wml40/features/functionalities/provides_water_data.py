from ml.ml40.features.functionalities.functionality import Functionality
from ml.wml40.features.properties.values.waterlevel import WaterLevel
from ml.wml40.features.properties.values.waterflow import WaterFlow


class ProvidesWaterData(Functionality):
    def __init__(self, namespace="wml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name: Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def getLatestLevel(self) -> WaterLevel:
        pass

    def getLevelDataSeries(self, startTime, endTime) -> [WaterLevel]:
        return "Dataseries Data is huge"

        
    def getLatestFlow(self) -> WaterFlow:
        pass

    def getFlowDataSeries(self, startTime, endTime) -> [WaterFlow]:
        pass
