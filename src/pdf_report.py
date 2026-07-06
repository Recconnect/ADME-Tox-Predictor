import io
import os
from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from src.i18n import t, translate_prop_name
from src.radar import compute_scores, plot_radar


_FONT_PATH: str | None = None
_FONTS_CANDIDATES = [
    "C:\\Windows\\Fonts\\arial.ttf",
    "C:\\Windows\\Fonts\\Arial.ttf",
    "C:\\Windows\\Fonts\\segoeui.ttf",
    "C:\\Windows\\Fonts\\SegoeUI.ttf",
    "C:\\Windows\\Fonts\\dejavusans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def _find_font() -> str | None:
    global _FONT_PATH
    if _FONT_PATH:
        return _FONT_PATH
    for p in _FONTS_CANDIDATES:
        if os.path.exists(p):
            _FONT_PATH = p
            return p
    return None


def _class_color(val: str) -> tuple[int, int, int]:
    green = (0, 150, 0)
    red = (200, 0, 0)
    orange = (200, 150, 0)
    neutral = (100, 100, 100)

    low = ["low", "low permeability", "low risk", "non-inhibitor", "non-mutagenic",
           "high bioavailability", "negative", "insoluble", "weakly bound"]
    high = ["high", "high permeability", "high risk", "inhibitor", "mutagenic",
            "low bioavailability", "positive", "soluble", "strongly bound", "highly bound",
            "moderately bound"]
    moderate = ["moderate", "moderately bound"]

    vl = val.lower().strip()
    if vl in low:
        return green
    if vl in high:
        return red
    if vl in moderate:
        return orange
    return neutral


class ADMEReport(FPDF):
    def __init__(self, lang: str = "ru"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.lang = lang
        self.set_auto_page_break(auto=True, margin=20)
        font_path = _find_font()
        if font_path:
            self.add_font("Uni", "", font_path)
            self.add_font("Uni", "B", font_path)
        else:
            self.add_font("Uni", "", "C:\\Windows\\Fonts\\arial.ttf")
            self.add_font("Uni", "B", "C:\\Windows\\Fonts\\arial.ttf")

    def _header(self):
        self.set_font("Uni", "B", 14)
        self.set_text_color(30, 60, 120)
        self.cell(0, 10, "ADMETox.AI", align="L")
        self.set_font("Uni", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, t("pdf_report", self.lang), align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 60, 120)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def _footer(self):
        self.set_y(-15)
        self.set_font("Uni", "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"ADMETox.AI — {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C")

    def add_title(self, smiles: str, canonical: str | None):
        self.set_font("Uni", "B", 12)
        self.set_text_color(30, 60, 120)
        self.cell(0, 8, t("pdf_molecule", self.lang), new_x="LMARGIN", new_y="NEXT")
        self.set_font("Courier", "", 9)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, f"SMILES: {smiles}", new_x="LMARGIN", new_y="NEXT")
        if canonical and canonical != smiles:
            self.cell(0, 5, f"Canonical: {canonical}", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def add_result_table(self, result: dict):
        self.set_font("Uni", "B", 11)
        self.set_text_color(30, 60, 120)
        self.cell(0, 7, t("pdf_properties", self.lang), new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        prop_keys = [
            "Solubility (logS)", "SolubilityClass",
            "Caco-2 Permeability", "Caco-2 Class",
            "hERG Toxicity Risk", "hERG Class",
            "Lipophilicity (logD)",
            "P-gp Inhibition", "P-gp Class",
            "CYP3A4 Inhibition", "CYP3A4 Class",
            "CYP2D6 Inhibition", "CYP2D6 Class",
            "Ames Mutagenicity", "Ames Class",
            "Bioavailability", "Bioavailability Class",
            "PPB (plasma binding)", "PPB Class",
        ]

        col_w = 80

        for key in prop_keys:
            val = result.get(key)
            if val is None:
                continue
            display = f"{val:.3f}" if isinstance(val, float) else str(val)
            label = translate_prop_name(key, self.lang)

            is_class = "Class" in key
            if is_class:
                bg = _class_color(str(val))
                self.set_text_color(*bg)
            else:
                self.set_text_color(0, 0, 0)

            self.set_font("Uni", "B" if is_class else "", 9)
            self.cell(col_w, 5, label, border=0)
            self.set_font("Courier", "", 9)
            self.cell(0, 5, display, border=0, new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(0, 0, 0)

        self.ln(3)

    def add_radar(self, result: dict):
        scores = compute_scores({k: v for k, v in result.items() if isinstance(v, (int, float))})
        if not any(s > 0 for s in scores):
            return
        fig = plot_radar(scores, self.lang)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
        buf.seek(0)
        self.set_font("Uni", "B", 11)
        self.set_text_color(30, 60, 120)
        self.cell(0, 7, t("pdf_radar", self.lang), new_x="LMARGIN", new_y="NEXT")
        self.image(buf, x=50, w=100)
        self.ln(3)


def generate_pdf(smiles: str, result: dict, lang: str = "ru") -> bytes:
    pdf = ADMEReport(lang)
    pdf.add_page()
    pdf.add_title(smiles, result.get("canonical_smiles"))
    pdf.add_result_table(result)
    pdf.add_radar(result)
    out = pdf.output()
    return bytes(out) if isinstance(out, bytearray) else out

