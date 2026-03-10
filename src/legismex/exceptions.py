class LegismexError(Exception):
    """Excepción base para todos los errores en legismex."""
    pass


class LegismexConnectionError(LegismexError):
    """
    Excepción lanzada cuando hay un error de conexión con el servidor 
    del Congreso o Periódico Oficial (ej. Timeout, SSL inválido no manejado).
    """
    pass


class HTMLParsingError(LegismexError):
    """
    Excepción lanzada cuando la estructura del HTML ha cambiado y 
    no se pueden encontrar los elementos esperados usando BeautifulSoup/lxml.
    """
    pass


class APIResponseError(LegismexError):
    """
    Excepción lanzada cuando el backend interconectado (JSON/REST)
    devuelve un status code de error (e.g. 500) o un payload inesperado.
    """
    pass


class DocumentNotFoundError(LegismexError):
    """
    Excepción lanzada cuando se busca una gaceta, iniciativa o documento 
    específico por parámetros (año, id) y no existe en los registros.
    """
    pass
