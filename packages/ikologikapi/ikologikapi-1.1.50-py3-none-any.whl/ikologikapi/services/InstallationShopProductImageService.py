import json
from types import SimpleNamespace

import requests

from ikologikapi.IkologikApiCredentials import IkologikApiCredentials
from ikologikapi.IkologikException import IkologikException
from ikologikapi.services.AbstractIkologikInstallationService import AbstractIkologikInstallationService


class InstallationShopProductImageService(AbstractIkologikInstallationService):

    def __init__(self, jwtHelper: IkologikApiCredentials):
        super().__init__(jwtHelper)

    # CRUD actions

    def get_url(self, customer, installation, shop_product) -> str:
        return f'{self.jwtHelper.get_url()}/api/v2/customer/{customer}/installation/{installation}/shopproduct/{shop_product}/shopproductimage'

    def get_by_id(self, customer: str, installation: str, shop_product: str, id: str, include_upload_url: bool = False, include_image_url: bool = False, include_view_url: bool = False, include_thumbnail_url: bool = False) -> object:
        try:
            params = {
                'includeUploadUrl': include_upload_url,
                'includeImageUrl': include_image_url,
                'includeViewUrl': include_view_url,
                'includeThumbnailUrl': include_thumbnail_url
            }
            response = requests.get(
                f'{self.get_url(customer, installation, shop_product)}/{id}',
                headers=self.get_headers(),
                params=params
            )
            if response.status_code == 200:
                result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                return result
            else:
                raise IkologikException("Error while performing get_by_id, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing get_by_id")

    def list(self, customer: str, installation: str, shop_product: str, include_upload_url: bool = False, include_image_url: bool = False, include_view_url: bool = False, include_thumbnail_url: bool = False) -> list:
        try:
            params = {
                'includeUploadUrl': include_upload_url,
                'includeImageUrl': include_image_url,
                'includeViewUrl': include_view_url,
                'includeThumbnailUrl': include_thumbnail_url
            }
            response = requests.get(
                f'{self.get_url(customer, installation, shop_product)}',
                headers=self.get_headers(),
                params=params
            )
            if response.status_code == 200:
                result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                return result
            else:
                raise IkologikException("Error while performing list, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing list")

    def search(self, customer: str, installation: str, shop_product: str, search, include_upload_url: bool = False, include_image_url: bool = False, include_view_url: bool = False, include_thumbnail_url: bool = False) -> list:
        try:
            params = {
                'includeUploadUrl': include_upload_url,
                'includeImageUrl': include_image_url,
                'includeViewUrl': include_view_url,
                'includeThumbnailUrl': include_thumbnail_url
            }
            data = json.dumps(search, default=lambda o: o.__dict__)
            response = requests.post(
                f'{self.get_url(customer, installation, shop_product)}/search',
                data=data,
                headers=self.get_headers(),
                params=params
            )
            if response.status_code == 200:
                result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                return result
            else:
                raise IkologikException("Error while performing search, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing search")

    def create(self, customer: str, installation: str, shop_product: str, o: object, include_upload_url: bool = False, include_image_url: bool = False, include_view_url: bool = False, include_thumbnail_url: bool = False) -> object:
        try:
            params = {
                'includeUploadUrl': include_upload_url,
                'includeImageUrl': include_image_url,
                'includeViewUrl': include_view_url,
                'includeThumbnailUrl': include_thumbnail_url
            }
            data = json.dumps(o, default=lambda o: o.__dict__)
            response = requests.post(
                self.get_url(customer, installation, shop_product),
                data=data,
                headers=self.get_headers(),
                params=params
            )
            if response.status_code == 201:
                result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                return result
            else:
                raise IkologikException("Error while performing create, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing create")

    def update(self, customer: str, installation: str, shop_product: str, o: object, include_upload_url: bool = False, include_image_url: bool = False, include_view_url: bool = False, include_thumbnail_url: bool = False) -> object:
        try:
            params = {
                'includeUploadUrl': include_upload_url,
                'includeImageUrl': include_image_url,
                'includeViewUrl': include_view_url,
                'includeThumbnailUrl': include_thumbnail_url
            }
            data = json.dumps(o, default=lambda o: o.__dict__)
            response = requests.put(
                f'{self.get_url(customer, installation, shop_product)}/{o.id}',
                data=data,
                headers=self.get_headers(),
                params=params
            )
            if response.status_code == 200:
                result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                return result
            else:
                raise IkologikException("Error while performing update, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing update")

    def delete(self, customer: str, installation: str, shop_product: str, id: str):
        try:
            response = requests.delete(
                f'{self.get_url(customer, installation, shop_product)}/{id}',
                headers=self.get_headers()
            )
            if response.status_code != 204:
                raise IkologikException("Error while performing delete, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing delete")

    # File actions

    def upload(self, customer: str, installation: str, shop_product: str, id: str) -> str:
        try:
            response = requests.get(
                f'{self.get_url(customer, installation, shop_product)}/{id}/upload',
                headers=self.get_headers()
            )
            if response.status_code == 200:
                result = response.content.decode("utf-8")
                return result
            else:
                raise IkologikException("Error while performing upload, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing upload")

    def prepare(self, customer: str, installation: str, shop_product: str, id: str) -> str:
        try:
            response = requests.get(
                f'{self.get_url(customer, installation, shop_product)}/{id}/prepare',
                headers=self.get_headers()
            )
            if response.status_code == 200:
                result = response.content.decode("utf-8")
                return result
            else:
                raise IkologikException("Error while performing prepare, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing upload")

    def image(self, customer: str, installation: str, shop_product: str, id: str) -> str:
        try:
            response = requests.get(
                f'{self.get_url(customer, installation, shop_product)}/{id}/download',
                headers=self.get_headers()
            )
            if response.status_code == 200:
                result = response.content.decode("utf-8")
                return result
            else:
                raise IkologikException("Error while performing download, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing upload")

    def view(self, customer: str, installation: str, shop_product: str, id: str) -> str:
        try:
            response = requests.get(
                f'{self.get_url(customer, installation, shop_product)}/{id}/view',
                headers=self.get_headers()
            )
            if response.status_code == 200:
                result = response.content.decode("utf-8")
                return result
            else:
                raise IkologikException("Error while performing view, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing upload")

    def thumbnail(self, customer: str, installation: str, shop_product: str, id: str) -> str:
        try:
            response = requests.get(
                f'{self.get_url(customer, installation, shop_product)}/{id}/thumbnail',
                headers=self.get_headers()
            )
            if response.status_code == 200:
                result = response.content.decode("utf-8")
                return result
            else:
                raise IkologikException("Error while performing download, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing upload")
