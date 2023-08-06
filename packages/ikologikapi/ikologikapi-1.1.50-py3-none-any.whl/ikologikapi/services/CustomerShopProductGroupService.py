from ikologikapi.IkologikApiCredentials import IkologikApiCredentials
from ikologikapi.services.AbstractIkologikCustomerService import AbstractIkologikCustomerService


class CustomerShopProductGroupService(AbstractIkologikCustomerService):

    def __init__(self, jwtHelper: IkologikApiCredentials):
        super().__init__(jwtHelper)

    # CRUD actions

    def get_url(self, customer) -> str:
        return f'{self.jwtHelper.get_url()}/api/v2/customer/{customer}/shopproductgroup'
