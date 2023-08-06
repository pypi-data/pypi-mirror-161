from ikologikapi.domain.AbstractIkologikInstallationFieldType import AbstractIkologikInstallationFieldType


class ReportTypeFieldType(AbstractIkologikInstallationFieldType):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)

        self.reportType = None
