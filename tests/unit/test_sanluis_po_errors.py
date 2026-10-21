import json

import httpx
import pytest
from pydantic import ValidationError

from legismex.sanluis_po import SanLuisPoClient


def publication(doc_id):
    return {
        "id": doc_id,
        "fecha_publicacion": "2026-10-20",
        "titulo": "Documento de prueba",
        "pdf": "documento.pdf",
    }


def edition_with_notice_response(notice_response):
    def handler(request):
        if "/aviso/" in request.url.path:
            if isinstance(notice_response, Exception):
                raise notice_response
            return notice_response
        return httpx.Response(
            200, json={"success": True, "nivel1": [publication(1)]}
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        return SanLuisPoClient(client=client).obtener_edicion_por_fecha("2026-10-20")


@pytest.mark.parametrize(
    ("response", "error"),
    [
        (httpx.Response(503), httpx.HTTPStatusError),
        (httpx.ReadTimeout("Tiempo agotado"), httpx.ReadTimeout),
        (httpx.Response(200, text="no es JSON"), json.JSONDecodeError),
        (
            httpx.Response(
                200, json={"success": True, "publicacionesAv": [{"id": 2}]}
            ),
            ValidationError,
        ),
    ],
)
def test_notice_errors_do_not_return_partial_edition(response, error):
    with pytest.raises(error):
        edition_with_notice_response(response)


def test_edition_contains_dispositions_and_notices():
    edition = edition_with_notice_response(
        httpx.Response(200, json={"success": True, "publicacionesAv": [publication(2)]})
    )
    assert [(doc.id, doc.es_aviso) for doc in edition.documentos] == [
        (1, False), (2, True)
    ]


def test_successful_empty_notices_preserve_dispositions():
    edition = edition_with_notice_response(
        httpx.Response(200, json={"success": True, "publicacionesAv": []})
    )
    assert [doc.id for doc in edition.documentos] == [1]
