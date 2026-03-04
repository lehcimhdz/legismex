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
]
