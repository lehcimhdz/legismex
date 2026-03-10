from bs4 import BeautifulSoup
from typing import List

from .models import SanLuisGaceta


class SanLuisParser:
    """Parser for the Gaceta Parlamentaria page of the Congreso de San Luis Potosí.

    The page is rendered by Drupal 7 using nested Field Collections:

    ``field-tl-gacetas-parlamentarias``  (one per month)
      └─ ``field-archivo-mes-tl-gacetas-par``  (one per session)
           ├─ nombre    (.field-nombre-arch-mes-tl-gpar)
           ├─ fecha     (.field-fecha-arch-mes-tl-gpar  → span.date-display-single)
           └─ PDFs      (.field-archivo-arch-mes-tl-gpar  → a[href])
    """

    BASE_URL = "https://congresosanluis.gob.mx"

    @staticmethod
    def parse_gacetas(html: str) -> List[SanLuisGaceta]:
        """Parse the full HTML of the gacetas page and return all sessions.

        Args:
            html: Raw HTML response from
                  ``/trabajo/trabajo-legislativo/gacetas-parlamentarias``.

        Returns:
            A flat list of :class:`SanLuisGaceta`, one per session,
            ordered chronologically as they appear on the page.
        """
        soup = BeautifulSoup(html, "html.parser")
        gacetas: List[SanLuisGaceta] = []

        # Each month group is a Drupal field-collection item on the outer level.
        month_groups = soup.find_all(
            "div",
            class_=lambda c: c and "field-collection-item-field-tl-gacetas-parlamentarias" in c,
        )

        for month_group in month_groups:
            # ── Month label ────────────────────────────────────────────────
            mes_span = month_group.find(
                "div", class_=lambda c: c and "field-mes-tl-gacetas-par" in c
            )
            mes = ""
            if mes_span:
                date_span = mes_span.find("span", class_="date-display-single")
                if date_span:
                    mes = date_span.get_text(strip=True)

            # ── Session items inside this month group ──────────────────────
            session_items = month_group.find_all(
                "div",
                class_=lambda c: c and "field-collection-item-field-archivo-mes-tl-gacetas-par" in c,
            )

            for session in session_items:
                # Nombre de la sesión
                nombre_div = session.find(
                    "div", class_=lambda c: c and "field-nombre-arch-mes-tl-gpar" in c
                )
                nombre = ""
                if nombre_div:
                    nombre = nombre_div.get_text(strip=True)

                # Fecha (ISO from content attr + human text)
                fecha_div = session.find(
                    "div", class_=lambda c: c and "field-fecha-arch-mes-tl-gpar" in c
                )
                fecha_iso = ""
                fecha_texto = ""
                if fecha_div:
                    date_span = fecha_div.find(
                        "span", class_="date-display-single")
                    if date_span:
                        fecha_iso = date_span.get("content", "")
                        fecha_texto = date_span.get_text(strip=True)

                # PDFs
                archivo_div = session.find(
                    "div", class_=lambda c: c and "field-archivo-arch-mes-tl-gpar" in c
                )
                urls_pdf: List[str] = []
                if archivo_div:
                    for a in archivo_div.find_all("a", href=True):
                        href = a["href"].strip()
                        # Keep only PDF links; resolve relative paths
                        if not href:
                            continue
                        if href.lower().endswith(".pdf") or "pdf" in href.lower():
                            if href.startswith("http"):
                                urls_pdf.append(href)
                            else:
                                urls_pdf.append(
                                    f"{SanLuisParser.BASE_URL}{href}"
                                    if href.startswith("/")
                                    else f"{SanLuisParser.BASE_URL}/{href}"
                                )

                if nombre or urls_pdf:
                    gacetas.append(
                        SanLuisGaceta(
                            mes=mes,
                            nombre=nombre,
                            fecha_iso=fecha_iso,
                            fecha_texto=fecha_texto,
                            urls_pdf=urls_pdf,
                        )
                    )

        return gacetas
