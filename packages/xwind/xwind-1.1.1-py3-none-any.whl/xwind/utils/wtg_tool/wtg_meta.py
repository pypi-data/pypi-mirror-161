from dataclasses import dataclass


@dataclass
class WTG_META:
    RotorDiameter: float = 0
    ManufactureName: str = 'HEWP'
    Description: str = ''
    Comments: str = ''
    FormatVersion: str = '1.01'
    ReferenceURI: str = ''
    ContextInformation: str = ''
    CertificateChecksum: str = ''
    SuggestedHeights: float = 80

    @property
    def Radius(self):
        return self.RotorDiameter / 2

    @Radius.setter
    def Radius(self, value):
        self.RotorDiameter = value * 2
