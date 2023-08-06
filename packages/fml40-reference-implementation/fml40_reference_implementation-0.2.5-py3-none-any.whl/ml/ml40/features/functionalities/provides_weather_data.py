from ml.ml40.features.functionalities.functionality import Functionality
from ml.ml40.features.properties.values.weatherdata import WeatherData


class ProvidesWeatherData(Functionality):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name: Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def getLatestWeatherData(self) -> WeatherData:
        pass

    def getWeatherDataSeries(self, startTime, endTime) -> [WeatherData]:
        pass
