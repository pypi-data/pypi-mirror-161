from ikologikapi.domain.AbstractIkologikCustomerObject import AbstractIkologikCustomerObject


class AbstractIkologikInstallationObject(AbstractIkologikCustomerObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer)

        self.installation = installation
