# Referencia de Modelos (Pydantic)

La librería serializa la información escrapeada en los siguientes modelos fuertemente tipados:

*   **`PeriodoVotacion`**: Representa un semestre o lapso (ej. "Primer periodo ordinario LXVI").
    *   `legislatura`: int
    *   `nombre`: str
    *   `url_base`: str
*   **`VotacionDetalle`**: Representa el acta de una votación particular, con saldos de votos si aplica.
    *   `fecha`: str
    *   `asunto`: str (Contiene la síntesis legislativa)
    *   `url_acta`: Optional[str]
    *   `url_pdf`: Optional[str]
    *   `votos_favor`: Optional[int]
    *   `votos_contra`: Optional[int]
    *   `abstenciones`: Optional[int]
*   **`Dictamen`**: Representa el resultado de búsqueda de un dictamen.
    *   `fecha`: str
    *   `titulo`: str
    *   `tramites`: str
    *   `url_gaceta`: Optional[str]
    *   `url_pdf`: Optional[str]
*   **`Proposicion`**: Similar a Iniciativa, con datos como: `fecha_presentacion`, `titulo`, `promovente`, `tramite_o_estado`, `aprobada`, `url_gaceta`, `url_pdf`.
*   **`DocumentoGaceta`**: Enlace estático para Asistencias, Agendas o Actas sumamente sencillo (`fecha_o_titulo`, `url_documento`).
*   **`ResultadoBusqueda`**: Un hit devuelto por el buscador interno.
    *   `palabra_clave`: str
    *   `fecha`: str
    *   `contexto`: str (Extracto textual donde aparece la palabra clave)
    *   `url_origen`: str
    *   `url_pdf`: Optional[str]
*   **`Iniciativa`**: Registro de seguimiento de una iniciativa particular.
    *   `fecha_presentacion`: str
    *   `titulo`: str
    *   `promovente`: str
    *   `tramite_o_estado`: str
    *   `url_gaceta`: Optional[str]
    *   `url_pdf`: Optional[str]
    *   `dictaminada`: bool

#### Modelos del Senado
*   **`GacetaSenado`**: Colección raíz de una gaceta diaria o de sesión (histórica o reciente).
    *   `titulo_edicion`: str
    *   `documentos`: List[DocumentoSenado]
*   **`DocumentoSenado`**: Instancia validada de un asunto publicado en Senado.
    *   `titulo`: str
    *   `url`: str
    *   `categoria`: str
*   **`ReferenciaGaceta`**: Referencia obtenida a través del calendario histórico.
    *   `fecha`: str
    *   `url`: str
    *   `descripcion`: str

#### Modelos del DOF
*   **`DofEdicion`**: Concentrado con todos los decretos y acuerdos del día.
    *   `fecha`: str
    *   `documentos`: List[DofDocumento]
*   **`DofDocumento`**: Instancia validada de una publicación gubernamental en el DOF.
    *   `seccion`: str
    *   `organismo`: str
    *   `dependencia`: str
    *   `titulo`: str
    *   `url`: str

#### Modelos de la CDMX
*   **`DocumentoCdmx`**: Representa un documento del archivo parlamentario o debate de la Ciudad de México.
    *   `titulo`: str
    *   `fecha`: str
    *   `peso_kb`: float
    *   `peso_etiqueta`: str
    *   `url_pdf`: str
*   **`GacetaConsejeria`**: Instancia local del portal de la Consejería operado bajo ZK Framework.
    *   `descripcion`: str
    *   `fecha`: str
    *   `numero`: str
    *   `tiene_pdf`: bool
    *   `tiene_indice`: bool
    *   `index_absoluto`: int

#### Modelos de Jalisco
*   **`JaliscoEvento`**: Evento registrado en el calendario (ej. Sesión de Pleno, Comisiones).
    *   `fecha`: str
    *   `titulo`: str
    *   `tipo`: int
    *   `id_evento`: int
    *   `puntos_orden`: List[JaliscoPunto]
*   **`JaliscoPunto`**: Punto individual dentro del orden del día de un evento.
    *   `titulo`: str
    *   `documentos`: List[JaliscoDocumento]
*   **`JaliscoDocumento`**: Documento final adjunto o embebido (pdf, docx).
    *   `titulo`: str
    *   `url`: str

#### Modelos del Periódico Oficial de Jalisco
*   **`JaliscoPoResumen`**: Vista previa de una edición en listas o búsquedas.
    *   `id_newspaper`: int
    *   `date_newspaper`: str
    *   `tomo`: str
    *   `number`: str
    *   `description`: str
*   **`JaliscoPoEdicion`**: Detalle definitivo de la publicación.
    *   `id`: int
    *   `post_date`: str
    *   `link`: str (Enlace directo al PDF)

#### Modelos de Nuevo León
*   **`NuevoLeonIniciativa`**: Propuesta de ley de los diputados del H. Congreso de Nuevo León.
    *   `expediente`: str
    *   `legislatura`: str
    *   `promovente`: str
    *   `asunto`: str
    *   `comision`: str
    *   `fecha`: str
    *   `estado`: str
    *   `url_pdf`: Optional[str]
*   **`NuevoLeonPoEdicion`**: Registro agrupado del Periódico Oficial (Estado de Nuevo León).
    *   `numero`: str
    *   `fecha`: str
    *   `urls_pdf`: List[str]
*   **`EdomexGaceta`**: Número de Gaceta Parlamentaria del Estado de México.
    *   `numero`: str
    *   `fecha`: str
    *   `url_pdf`: str

#### Modelos de Puebla
*   **`PueblaGaceta`**: Gaceta legislativa mensual del Congreso de Puebla.
    *   `mes`: str
    *   `numero`: str
    *   `fecha_texto`: str
    *   `url_pdf`: str
    *   `legislatura`: str
    *   `anio_legislativo`: Optional[str]
