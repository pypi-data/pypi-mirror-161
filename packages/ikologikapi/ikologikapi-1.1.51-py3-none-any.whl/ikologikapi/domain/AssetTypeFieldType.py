from ikologikapi.domain.AbstractIkologikCustomerFieldType import AbstractIkologikCustomerFieldType


class AssetTypeFieldType(AbstractIkologikCustomerFieldType):

    def __init__(self, customer: str):
        super().__init__(customer)

        self.assetType = None
