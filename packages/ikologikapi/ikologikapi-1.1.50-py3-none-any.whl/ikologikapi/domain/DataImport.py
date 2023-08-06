from ikologikapi.domain.AbstractIkologikInstallationObject import AbstractIkologikInstallationObject


class DataImport(AbstractIkologikInstallationObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)

        self.name = None
        self.status = None
        self.active = True
        self.parameters = []
