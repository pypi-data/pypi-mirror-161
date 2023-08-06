from ikologikapi.domain.AbstractIkologikInstallationObject import AbstractIkologikInstallationObject


class InstallationShopProductGroup(AbstractIkologikInstallationObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)

        self.code = None
        self.name = None
