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
from .chiapas_gaceta import ChiapasGaceta, ChiapasGacetaClient
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
from .sanluis_po import SanLuisPoClient, SanLuisPoEdicion, SanLuisPoDocumento
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
    SinaloaDictamen,
    SinaloaAcuerdo,
    SinaloaDecreto,
    SinaloaLegislatura,
)
from .sinaloa_po import SinaloaPoClient, SinaloaPoEdicion
from .sonora import (
    SonoraClient,
    SonoraGaceta,
    SonoraLegislatura,
    SonoraGacetaMedia,
)
from .durango_gaceta import DurangoGacetaClient, DurangoGaceta
from .durango_po import DurangoPoClient, DurangoPoEdicion
from .hidalgo_gaceta import (
    HidalgoGacetaClient,
    HidalgoGaceta,
    HidalgoDocumento,
    HidalgoGacetaDetalle,
)
from .sonora_po import SonoraPoClient, SonoraPoEdicion, SonoraPoResultado
from .bc_po import BcPoClient, BcPoEdicion, BcPoResultado
from .bc_congreso import BcCongresoClient, BcIniciativa
from .bcs_po import BcsPoClient, BcsPoEdicion
from .bcs_congreso import (
    BcsCongresoClient,
    BcsSesion,
    BcsDocumento,
    BcsOrdenDia,
    BcsActa,
    BcsDiario,
)
from .hidalgo_po import HidalgoPoClient, HidalgoPoEdicion, HidalgoPoResultado
from .zacatecas import ZacatecasClient, ZacatecasGaceta
from .zacatecas_po import ZacatecasPoClient, ZacatecasPoPublicacion
from .yucatan_congreso import YucatanCongresoClient, YucatanIniciativa, YucatanDocumento
from .yucatan_po import YucatanPoClient, YucatanPoEdicion
from .chihuahua_congreso import ChihuahuaCongresoClient, ChihuahuaSesion, ChihuahuaDocumento

__all__ = [
    # Durango
    "DurangoGacetaClient",
    "DurangoGaceta",
    "DurangoPoClient",
    "DurangoPoEdicion",

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

    # Chiapas - Gaceta
    "ChiapasGaceta",
    "ChiapasGacetaClient",

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

    # San Luis Potosí - Congreso
    "SanLuisClient",
    "SanLuisGaceta",

    # San Luis Potosí - PO
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
    "SinaloaDictamen",
    "SinaloaAcuerdo",
    "SinaloaDecreto",
    "SinaloaLegislatura",

    # Sinaloa - Periódico Oficial
    "SinaloaPoClient",
    "SinaloaPoEdicion",

    # Sonora - Gaceta Parlamentaria
    "SonoraClient",
    "SonoraGaceta",
    "SonoraLegislatura",
    "SonoraGacetaMedia",

    # Hidalgo - Gaceta
    "HidalgoGacetaClient",
    "HidalgoGaceta",
    "HidalgoDocumento",
    "HidalgoGacetaDetalle",

    # Sonora - Periódico Oficial
    "SonoraPoClient",
    "SonoraPoEdicion",
    "SonoraPoResultado",

    # Baja California - PO
    "BcPoClient",
    "BcPoEdicion",
    "BcPoResultado",

    # Baja California - Congreso
    "BcCongresoClient",
    "BcIniciativa",

    # Baja California Sur - Congreso
    "BcsCongresoClient",
    "BcsSesion",
    "BcsDocumento",
    "BcsOrdenDia",
    "BcsActa",
    "BcsDiario",

    # Hidalgo - Periódico Oficial
    "HidalgoPoClient",
    "HidalgoPoEdicion",
    "HidalgoPoResultado",

    # Zacatecas - Congreso
    "ZacatecasClient",
    "ZacatecasGaceta",

    # Zacatecas - PO
    "ZacatecasPoClient",
    "ZacatecasPoPublicacion",

    # Baja California Sur - PO
    "BcsPoClient",
    "BcsPoEdicion",

    # Yucatán - Congreso
    "YucatanCongresoClient",
    "YucatanIniciativa",
    "YucatanDocumento",

    # Yucatán - Periódico Oficial
    "YucatanPoClient",
    "YucatanPoEdicion",

    # Chihuahua - Congreso
    "ChihuahuaCongresoClient",
    "ChihuahuaSesion",
    "ChihuahuaDocumento",
]
