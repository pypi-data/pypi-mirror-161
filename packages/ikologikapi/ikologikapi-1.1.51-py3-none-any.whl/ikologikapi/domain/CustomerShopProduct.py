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
        self.descriptionTranslations = dict({})
        self.detailedDescription = None
        self.detailedDescriptionTranslations = dict({})
        self.unit = None
        self.unitTranslations = dict({})
