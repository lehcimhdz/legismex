from .gaceta import GacetaClient, Iniciativa, DictamenesIndex, Dictamen, DocumentoGaceta, Proposicion
from .senado import SenadoClient, SenadoGaceta, SenadoResumen
from .dof import DofClient, DofEdicion, DofDocumento
from .cdmx import CdmxClient, DocumentoCdmx
from .consejeria import ConsejeriaClient, ConsejeriaDocumento
from .jalisco import JaliscoClient, JaliscoEvent
from .jalisco_po import JaliscoPoClient, JaliscoPoEdicion
from .nuevoleon import NuevoLeonClient, NuevoLeonDictamen, NuevoLeonIniciativa
from .nuevoleon_po import NuevoLeonPoClient, NuevoLeonPoEdicion, NuevoLeonPoOrden
from .edomex import EdomexClient, EdomexIniciativa, EdomexPuntoAcuerdo, EdomexPronunciamiento
from .edomex_po import EdomexPoClient, EdomexPoEdicion, EdomexPoDocumento
from .puebla import PueblaClient, PueblaGaceta
from .puebla_po import PueblaPoClient, PueblaPoPaginacion, PueblaPoEdicion

__all__ = [
    # Gaceta Parlamentaria
    "GacetaClient",
    "Iniciativa",
    "DictamenesIndex",
    "Dictamen",
    "DocumentoGaceta",
    "Proposicion",
    
    # Senado
    "SenadoClient",
    "SenadoGaceta",
    "SenadoResumen",
    
    # DOF
    "DofClient",
    "DofEdicion",
    "DofDocumento",
    
    # CDMX - Congreso
    "CdmxClient",
    "DocumentoCdmx",
    
    # CDMX - Consejería
    "ConsejeriaClient",
    "ConsejeriaDocumento",

    # Jalisco - Congreso
    "JaliscoClient",
    "JaliscoEvent",

    # Jalisco - PO
    "JaliscoPoClient",
    "JaliscoPoEdicion",

    # Nuevo León - Congreso
    "NuevoLeonClient",
    "NuevoLeonDictamen",
    "NuevoLeonIniciativa",

    # Nuevo León - PO
    "NuevoLeonPoClient",
    "NuevoLeonPoEdicion",
    "NuevoLeonPoOrden",

    # Estado de México - Congreso
    "EdomexClient",
    "EdomexIniciativa",
    "EdomexPuntoAcuerdo",
    "EdomexPronunciamiento",

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
]
