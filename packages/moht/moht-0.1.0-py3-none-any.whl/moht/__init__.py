from logging import getLogger
from os import name
from platform import architecture, uname, python_implementation, python_version
from sys import platform

from moht.log import config_logger

LOG = getLogger(__name__)
config_logger(logger=LOG, verbose=False)
LOG.debug(f'Arch: {name} / {platform} / {" / ".join(architecture())}')
LOG.debug(f'Python: {python_implementation()}-{python_version()}')
LOG.debug(f'{uname()}')

VERSION = '0.1.0'
PLUGINS2CLEAN = [
    "Abandoned_Flatv2_0.esp", "Almalexia_Voicev1.esp", "FLG - Balmora's Underworld V1.1.esp", "BitterAndBlighted.ESP", "Building Up Uvirith's Legacy1.1.ESP",
    "Caldera.esp", "DD_Caldera_Expansion.esp", "NX9_Guards_Complete.ESP", "Radiant Gem.esp", "Dwemer and Ebony Service Refusal.ESP",
    "Foyada Mamaea Overhaul.ESP", "Graphic Herbalism.esp", "Graphic Herbalism - No Glow.esp", "Graphic Herbalism Extra.esp", "Hla Oad.esp",
    "CultSheog-1.02.ESP", "CultSheog-TR1807.esp", "Kilcunda's Balmora.ESP", "MD_Azurian Isles.esm", "Magical Missions.ESP", "Mannequins for Sale.esp",
    "Xenn's Marksman Overhaul.ESP", "Meteorite Ministry Palace - Higher.ESP", "MW Containers Animated.esp", "Go To Jail.esp",
    "Go To Jail (Mournhold + Solshteim).ESP", "MRM.esm", "NX9_Guards_Complete.ESP", "OAAB - The Ashen Divide.ESP", "On the Move.esp",
    "Ports Of Vvardenfell V1.6.ESP", "Quill of Feyfolken 2.0.esp", "Library of Vivec Overhaul - Full.esp", "SadrithMoraExpandedTR.esp", "Sanctus Shrine.esp",
    "DA_Sobitur_Facility_Clean.ESP", "DA_Sobitur_Quest_Part_1 Clean.esp", "DA_Sobitur_Quest_Part_2 Clean.esp", "DA_Sobitur_Repurposed_1.ESP",
    "DA_Sobitur_TRIngred_Compat.ESP", "Stav_gnisis_minaret.ESP", "OTR_Coast_Variety.esp", "TheForgottenShields - Artifacts_NG.esp", "SG-toughersixth.esp",
    "Ttooth's Missing NPCs - No Nolus.ESP", "True_Lights_And_Darkness_1.1.esp", "UCNature.esm", "UFR_v3dot2_noRobe.esp", "Vurt's BC Tree Replacer II.ESP",
    "Windows Glow - Bloodmoon Eng.esp", "Windows Glow - Raven Rock Eng.esp", "Windows Glow - Tribunal Eng.esp", "Windows Glow.esp",
]
