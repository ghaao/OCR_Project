from enum import Enum, auto

class DTC(Enum):
    """(Document Type Code) An enum that defines all available document type. 
        Attributes:
        MEDICAL_CERTIFICATE: Extract rrm, custNo, regNo, disease Classification Code, hospNm, DrNm and accsClssCd from a medical certificate.
        MEDICAL_RECEIPT: Extract period and medical expenses from a medical certificate.       
    """
    MEDICAL_CERTIFICATE = auto()
    MEDICAL_RECEIPT = auto()

class ITC(Enum):
    """(Image Type Mode) An enum that defines all available image type. 
        Attributes:
        SCAN: Clean image from scanner device
        PHOTO: Photo image from mobile device
    """
    SCAN = auto()
    PHOTO = auto()

class RM(Enum):
    """(Run Mode) An enum that defines all available run type. 
        Attributes:
        LOCAL_TEST: local pc test mode
        WEB_TEST: gui test mode
        PROD: run prod mode
    """
    LOCAL_TEST = auto()
    WEB_TEST = auto()
    PROD = auto()

    def __str__(self):
        return 'Spoiler engine is set to {0} mode.  '.format(self.name)

class MTM(Enum):
    """(Mapping Type Mode) An enum that defines all available mapping type. 
        Attributes:
        SINGLE_WORD: Single word mapping (ex.MEDICAL_RECEIPT)
        NUMERIC: word, number pair mapping
    """
    SINGLE_WORD = auto()
    NUMERIC = auto()