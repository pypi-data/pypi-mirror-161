from ikologikapi.domain.AbstractIkologikCustomerObject import AbstractIkologikCustomerObject


class CustomerShopProductImage(AbstractIkologikCustomerObject):

    def __init__(self, customer: str):
        super().__init__(customer)

        self.shopProduct = None

        self.order = None
        self.fileName = None
        self.fileSize = None

        self.prepared = False

        self.uploadUrl = None
        self.imageUrl = None
        self.viewUrl = None
        self.thumbnailUrl = None
