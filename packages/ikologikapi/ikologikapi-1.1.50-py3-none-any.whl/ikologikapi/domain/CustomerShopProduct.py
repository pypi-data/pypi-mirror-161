from ikologikapi.domain.AbstractIkologikCustomerObject import AbstractIkologikCustomerObject


class CustomerShopProduct(AbstractIkologikCustomerObject):

    def __init__(self, customer: str):
        super().__init__(customer)

        self.code = None
        self.groups = None
        self.pids = None
        self.quantity = None
        self.price = None
        self.rate = None

        self.description = None
        self.descriptionTranlations = dict({})
        self.detailedDescription = None
        self.detailedDescriptionTranlations = dict({})
        self.unit = None
        self.unitTranlations = dict({})
