from ml.ml40.features.functionalities.functionality import Functionality
from ml.wml40.features.properties.values.waterquality import WaterQuality


class ProvidesWaterQualityData(Functionality):
    def __init__(self, namespace="wml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name: Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def getQualityTimeSeries(self, startTime, endTime) -> [WaterQuality]:
        pass

        
