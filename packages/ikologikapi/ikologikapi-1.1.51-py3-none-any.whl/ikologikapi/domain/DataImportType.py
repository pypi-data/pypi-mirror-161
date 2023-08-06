from ikologikapi.domain.AbstractIkologikInstallationObject import AbstractIkologikInstallationObject


class DataImportType(AbstractIkologikInstallationObject):

    def __init__(self, customer: str, installation: str):
        super().__init__(customer, installation)

        self.name = None
        self.type = None
        self.active = True
        self.parameters = []
        self.mapping = DataImportTypeMapping()


class DataImportTypeMapping(object):

    def __init__(self):
        self.tags = []


class DataImportMappingTag(object):
    def __init__(self):
        self.sourceId = None
        self.sourceName = None
        self.sourceDataType = None
        self.sourceDescription = None
        self.tag = None
