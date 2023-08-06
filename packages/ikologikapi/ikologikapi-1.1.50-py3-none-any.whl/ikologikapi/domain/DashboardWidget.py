from ikologikapi.domain.AbstractIkologikInstallationObject import AbstractIkologikInstallationObject


class DashboardWidget(AbstractIkologikInstallationObject):

    def __init__(self, customer: str, installation: str, dashboard: str):
        super().__init__(customer, installation)

        self.dashboard = dashboard
        self.dashboardWidgetType = None
        self.type = None
        self.order = None
        self.parameters = []


class Parameter(object):

    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value
