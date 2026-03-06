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
from .chiapas_po import ChiapasPoClient, ChiapasPoEdicion, ChiapasAdministracion
from .sanluis import SanLuisClient, SanLuisGaceta
from .tabasco_iniciativas import TabascoIniciativasClient, TabascoIniciativa
from .tamaulipas import TamaulipasClient, TamaulipasGaceta
from .tamaulipas_po import TamaulipasPoClient, TamaulipasPoEdicion, TamaulipasPoDocumento
from .veracruz import VeracruzClient, VeracruzSesion, VeracruzDocumento
from .veracruz_po import VeracruzPoClient, VeracruzPoEdicion

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

    # Chiapas - PO
    "ChiapasPoClient",
    "ChiapasPoEdicion",
    "ChiapasAdministracion",
    
    # San Luis Potosí - Congreso y PO
    "SanLuisClient",
    "SanLuisGaceta",
    "SanLuisPoClient",
    "SanLuisPoEdicion",
    "SanLuisPoDocumento",

    # Tabasco - Iniciativas
    "TabascoIniciativasClient",
    "TabascoIniciativa",

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
]
