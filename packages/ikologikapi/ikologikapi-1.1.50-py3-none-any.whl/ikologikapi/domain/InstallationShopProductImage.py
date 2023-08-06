from ikologikapi.domain.AbstractIkologikInstallationObject import AbstractIkologikInstallationObject


class InstallationShopProductImage(AbstractIkologikInstallationObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)

        self.shopProduct = None

        self.order = None
        self.fileName = None
        self.fileSize = None

        self.prepared = False

        self.uploadUrl = None
        self.imageUrl = None
        self.viewUrl = None
        self.thumbnailUrl = None
