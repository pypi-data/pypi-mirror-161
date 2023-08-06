from ikologikapi.domain.AbstractIkologikInstallationObject import AbstractIkologikInstallationObject


class Asset(AbstractIkologikInstallationObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)

        self.assetType = None
        self.parent = None
        self.code = None
        self.name = None
        self.active = None
        self.fields = None
