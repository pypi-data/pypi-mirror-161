from ml.wml40.roles.dts.water.water import Water


class WaterReservoir(Water):
    def __init__(self, namespace="wml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
