from ikologikapi.IkologikApiCredentials import IkologikApiCredentials
from ikologikapi.services.AlertService import AlertService
from ikologikapi.services.AlertTypeService import AlertTypeService
from ikologikapi.services.AssetService import AssetService
from ikologikapi.services.AssetTypeFieldTypeService import AssetTypeFieldTypeService
from ikologikapi.services.AssetTypeService import AssetTypeService
from ikologikapi.services.BatchService import BatchService
from ikologikapi.services.BatchTypeService import BatchTypeService
from ikologikapi.services.CustomerService import CustomerService
from ikologikapi.services.CustomerShopProductImageService import CustomerShopProductImageService
from ikologikapi.services.DashboardService import DashboardService
from ikologikapi.services.DashboardWidgetService import DashboardWidgetService
from ikologikapi.services.DashboardWidgetTypeService import DashboardWidgetTypeService
from ikologikapi.services.DataImportService import DataImportService
from ikologikapi.services.DataImportTypeService import DataImportTypeService
from ikologikapi.services.GraphService import GraphService
from ikologikapi.services.InstallationService import InstallationService
from ikologikapi.services.InstallationShopProductGroupService import InstallationShopProductGroupService
from ikologikapi.services.InstallationShopProductService import InstallationShopProductService
from ikologikapi.services.MaintenanceTaskService import MaintenanceTaskService
from ikologikapi.services.MaintenanceTypeService import MaintenanceTypeService
from ikologikapi.services.MaintenanceTypeFieldTypeService import MaintenanceTypeFieldTypeService
from ikologikapi.services.CustomerShopProductGroupService import CustomerShopProductGroupService
from ikologikapi.services.InstallationShopProductImageService import InstallationShopProductImageService
from ikologikapi.services.CustomerShopProductService import CustomerShopProductService
from ikologikapi.services.ReportService import ReportService
from ikologikapi.services.ReportTypeService import ReportTypeService
from ikologikapi.services.TagAlertTypeService import TagAlertTypeService
from ikologikapi.services.TagService import TagService


class IkologikAPI:

    def __init__(self, url: str, username: str, password: str):
        self.apiCredentials = IkologikApiCredentials(url, username, password)
        self.alert = AlertService(self.apiCredentials)
        self.alertType = AlertTypeService(self.apiCredentials)
        self.asset = AssetService(self.apiCredentials)
        self.assetType = AssetTypeService(self.apiCredentials)
        self.assetTypeFieldType = AssetTypeFieldTypeService(self.apiCredentials)
        self.batch = BatchService(self.apiCredentials)
        self.batchType = BatchTypeService(self.apiCredentials)
        self.customer = CustomerService(self.apiCredentials)
        self.customerShopProduct = CustomerShopProductService(self.apiCredentials)
        self.customerShopProductImage = CustomerShopProductImageService(self.apiCredentials)
        self.customerShopProductGroup = CustomerShopProductGroupService(self.apiCredentials)
        self.dashboard = DashboardService(self.apiCredentials)
        self.dashboardWidget = DashboardWidgetService(self.apiCredentials)
        self.dashboardWidgetType = DashboardWidgetTypeService(self.apiCredentials)
        self.dataImport = DataImportService(self.apiCredentials)
        self.dataImportType = DataImportTypeService(self.apiCredentials)
        self.graph = GraphService(self.apiCredentials)
        self.installation = InstallationService(self.apiCredentials)
        self.installationShopProduct = InstallationShopProductService(self.apiCredentials)
        self.installationShopProductImage = InstallationShopProductImageService(self.apiCredentials)
        self.installationShopProductGroup = InstallationShopProductGroupService(self.apiCredentials)
        self.maintenanceTask = MaintenanceTaskService(self.apiCredentials)
        self.maintenanceType = MaintenanceTypeService(self.apiCredentials)
        self.maintenanceTypeFieldType = MaintenanceTypeFieldTypeService(self.apiCredentials)
        self.report = ReportService(self.apiCredentials)
        self.reportType = ReportTypeService(self.apiCredentials)
        self.tag = TagService(self.apiCredentials)
        self.tagAlertType = TagAlertTypeService(self.apiCredentials)

    def login(self):
        return self.apiCredentials.get_jwt()
