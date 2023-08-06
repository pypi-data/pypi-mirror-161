from ikologikapi.domain.AbstractIkologikInstallationObject import AbstractIkologikInstallationObject


class Dashboard(AbstractIkologikInstallationObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)

        self.name = None
