from ikologikapi.domain.AbstractIkologikCustomerObject import AbstractIkologikCustomerObject

class Asset(AbstractIkologikCustomerObject):

    def __init__(self, customer: str):
        super().__init__(customer)

        self.code = None
        self.name = None
        self.description = None
