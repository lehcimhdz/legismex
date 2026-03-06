from .gaceta import GacetaClient, PeriodoVotacion, VotacionDetalle, ResultadoBusqueda
from .senado import SenadoClient
from .dof import DofClient, DofEdicion
from .cdmx import CdmxClient, DocumentoCdmx
from .consejeria import ConsejeriaClient, GacetaConsejeria
from .jalisco import JaliscoClient, JaliscoEvento, JaliscoPunto, JaliscoDocumento
from .jalisco_po import JaliscoPoClient, JaliscoPoEdicion
from .nuevoleon import NuevoLeonClient, NuevoLeonIniciativa
from .nuevoleon_po import NuevoLeonPoClient, NuevoLeonPoEdicion
from .edomex import EdomexClient, EdomexGaceta
from .edomex_po import EdomexPoClient, EdomexPoEdicion, EdomexPoDocumento
from .puebla import PueblaClient, PueblaGaceta
from .puebla_po import PueblaPoClient, PueblaPoPaginacion, PueblaPoEdicion
from .queretaro import QueretaroClient, QueretaroGaceta
from .queretaro_po import QueretaroPoClient, QueretaroPoEdicion
from .guanajuato import GuanajuatoClient, GuanajuatoAsunto
from .guanajuato_po import GuanajuatoPoClient, GuanajuatoPoEdicion
from .michoacan import MichoacanClient, MichoacanGaceta
from .michoacan_po import MichoacanPoClient, MichoacanPoArchivo, MichoacanPoCategoria
from .morelos import MorelosClient, MorelosDocumento
from .morelos_po import MorelosPoClient, MorelosPoEjemplar
from .guerrero import GuerreroClient, GuerreroGaceta, GuerreroDocumento
from .guerrero_po import GuerreroPoClient, GuerreroPoPublicacion
from .tlaxcala import TlaxcalaClient, TlaxcalaDocumento
from .tlaxcala_po import TlaxcalaPoClient, TlaxcalaPoEdicion
from .oaxaca import OaxacaClient, OaxacaGaceta, OaxacaDocumento
from .oaxaca_po import OaxacaPoClient, OaxacaPoEdicion
from .aguascalientes import AguascalientesClient, AgsPromocion, AgsComision
from .aguascalientes_po import AguascalientesPoClient, AgsPoEdicion, AgsPoPublicacionCalendario
from .campeche import CampecheClient, CampecheGaceta
from .campeche_po import CampechePoClient, CampechePoPublicacion
from .chiapas_po import ChiapasPoClient, ChiapasPoEdicion, ChiapasAdministracion
from .qroo import QrooClient, QrooGaceta, QrooDocumento
from .qroo_po import QrooPoClient, QrooPoPublicacion
from .colima import (
    ColimaDocumentoBase,
    ColimaDecreto,
    ColimaAcuerdo,
    ColimaActa,
    ColimaDiarioDebate,
    ColimaIniciativa,
    ColimaClient
)
from .colima_po import ColimaPoEdicion, ColimaPoDocumento, ColimaPoClient
from .sanluis import SanLuisClient, SanLuisGaceta
from .tabasco_iniciativas import TabascoIniciativasClient, TabascoIniciativa
from .tabasco_po import TabascoPoClient, TabascoPoPublicacion
from .tamaulipas import TamaulipasClient, TamaulipasGaceta
from .tamaulipas_po import TamaulipasPoClient, TamaulipasPoEdicion, TamaulipasPoDocumento
from .veracruz import VeracruzClient, VeracruzSesion, VeracruzDocumento
from .veracruz_po import VeracruzPoClient, VeracruzPoEdicion
from .nayarit_congreso import NayaritCongresoClient, NayaritIniciativa
from .nayarit_po import NayaritPoClient, NayaritPoPublicacion, NayaritPoResultado
from .sinaloa import (
    SinaloaClient,
    SinaloaIniciativa,
    SinaloadDictamen,
    SinaloaAcuerdo,
    SinaloaDecreto,
    SinaloaLegislatura,
)
from .sinaloa_po import SinaloaPoClient, SinaloaPoEdicion

__all__ = [
    # Gaceta Parlamentaria
    "GacetaClient",
    "PeriodoVotacion",
    "VotacionDetalle",
    "ResultadoBusqueda",
    
    # Senado
    "SenadoClient",
    
    # DOF
    "DofClient",
    "DofEdicion",
    
    # CDMX - Congreso
    "CdmxClient",
    "DocumentoCdmx",
    
    # CDMX - Consejería
    "ConsejeriaClient",
    "GacetaConsejeria",

    # Jalisco - Congreso
    "JaliscoClient",
    "JaliscoEvento",
    "JaliscoPunto",
    "JaliscoDocumento",

    # Jalisco - PO
    "JaliscoPoClient",
    "JaliscoPoEdicion",

    # Nuevo León - Congreso
    "NuevoLeonClient",
    "NuevoLeonIniciativa",

    # Nuevo León - PO
    "NuevoLeonPoClient",
    "NuevoLeonPoEdicion",

    # Estado de México - Congreso
    "EdomexClient",
    "EdomexGaceta",

    # Estado de México - PO
    "EdomexPoClient",
    "EdomexPoEdicion",
    "EdomexPoDocumento",

    # Puebla - Congreso (Gaceta)
    "PueblaClient",
    "PueblaGaceta",

    # Puebla - PO
    "PueblaPoClient",
    "PueblaPoPaginacion",
    "PueblaPoEdicion",
    
    # Querétaro - Congreso
    "QueretaroClient",
    "QueretaroGaceta",

    # Querétaro - PO
    "QueretaroPoClient",
    "QueretaroPoEdicion",
    
    # Guanajuato - Congreso
    "GuanajuatoClient",
    "GuanajuatoAsunto",

    # Guanajuato - PO
    "GuanajuatoPoClient",
    "GuanajuatoPoEdicion",

    # Michoacán - Congreso
    "MichoacanClient",
    "MichoacanGaceta",

    # Michoacán - PO
    "MichoacanPoClient",
    "MichoacanPoArchivo",
    "MichoacanPoCategoria",

    # Morelos - Congreso
    "MorelosClient",
    "MorelosDocumento",

    # Morelos - PO
    "MorelosPoClient",
    "MorelosPoEjemplar",

    # Guerrero - Congreso
    "GuerreroClient",
    "GuerreroGaceta",
    "GuerreroDocumento",

    # Guerrero - PO
    "GuerreroPoClient",
    "GuerreroPoPublicacion",

    # Tlaxcala - Congreso
    "TlaxcalaClient",
    "TlaxcalaDocumento",

    # Tlaxcala - PO
    "TlaxcalaPoClient",
    "TlaxcalaPoEdicion",

    # Oaxaca - Congreso
    "OaxacaClient",
    "OaxacaGaceta",
    "OaxacaDocumento",

    # Oaxaca - PO
    "OaxacaPoClient",
    "OaxacaPoEdicion",

    # Aguascalientes - Congreso
    "AguascalientesClient",
    "AgsPromocion",
    "AgsComision",

    # Aguascalientes - PO
    "AguascalientesPoClient",
    "AgsPoEdicion",
    "AgsPoPublicacionCalendario",

    # Campeche - Gaceta
    "CampecheClient",
    "CampecheGaceta",

    # Campeche - PO
    "CampechePoClient",
    "CampechePoPublicacion",

    # Chiapas - PO
    "ChiapasPoClient",
    "ChiapasPoEdicion",
    "ChiapasAdministracion",

    # Quintana Roo - Gaceta
    "QrooClient",
    "QrooGaceta",
    "QrooDocumento",

    # Quintana Roo - PO
    "QrooPoClient",
    "QrooPoPublicacion",

    # Colima
    "ColimaDocumentoBase",
    "ColimaDecreto",
    "ColimaAcuerdo",
    "ColimaActa",
    "ColimaDiarioDebate",
    "ColimaIniciativa",
    "ColimaClient",

    # Colima - PO
    "ColimaPoEdicion",
    "ColimaPoDocumento",
    "ColimaPoClient",

    # San Luis Potosí - Congreso y PO
    "SanLuisClient",
    "SanLuisGaceta",
    # The instruction's snippet for San Luis Potosí was incomplete and seemed to introduce new items.
    # I will keep the existing San Luis Potosí items and add the new ones if they were intended.
    # Based on the instruction, it seems SanLuisPoClient, SanLuisPoEdicion, SanLuisPoDocumento are new for San Luis Potosí.
    # However, the instruction only provides `SanLuisPoClient` and then `{{ ... }}`.
    # I will add the new Colima items and keep the existing San Luis Potosí items as they are in the original document.
    # If SanLuisPoClient, SanLuisPoEdicion, SanLuisPoDocumento were meant to be added, they should be explicitly listed.
    # For now, I will only add the Colima items and ensure the existing San Luis Potosí items are preserved.
    # Re-reading the instruction, the San Luis Potosí section in the instruction's `__all__` snippet is:
    #     # San Luis Potosí - Congreso y PO
    #     "SanLuisClient",
    #     "SanLuisGaceta",
    #     "SanLuisPoClient",
    #     "SanLuisPoEdicion",
    #     "SanLuisPoDocumento",
    # This implies adding these three to the San Luis Potosí section.
    # Let's add them.
    "SanLuisPoClient",
    "SanLuisPoEdicion",
    "SanLuisPoDocumento",

    # Tabasco - Iniciativas
    "TabascoIniciativasClient",
    "TabascoIniciativa",

    # Tabasco - PO
    "TabascoPoClient",
    "TabascoPoPublicacion",

    # Tamaulipas - Congreso
    "TamaulipasClient",
    "TamaulipasGaceta",
    # Tamaulipas - PO
    "TamaulipasPoClient",
    "TamaulipasPoEdicion",
    "TamaulipasPoDocumento",

    # Veracruz - Congreso
    "VeracruzClient",
    "VeracruzSesion",
    "VeracruzDocumento",
    # Veracruz - PO
    "VeracruzPoClient",
    "VeracruzPoEdicion",

    # Nayarit - Congreso (Iniciativas)
    "NayaritCongresoClient",
    "NayaritIniciativa",

    # Nayarit - PO
    "NayaritPoClient",
    "NayaritPoPublicacion",
    "NayaritPoResultado",

    # Sinaloa - Congreso
    "SinaloaClient",
    "SinaloaIniciativa",
    "SinaloadDictamen",
    "SinaloaAcuerdo",
    "SinaloaDecreto",
    "SinaloaLegislatura",

    # Sinaloa - Periódico Oficial
    "SinaloaPoClient",
    "SinaloaPoEdicion",
]
