import json
from pathlib import Path


OUTPUT_PATH = Path("data/exams.json")


COMMON_EXAMS = [
    "Hemograma Completo",
    "Glicemia em Jejum",
    "Hemoglobina Glicada",
    "Colesterol Total",
    "Colesterol HDL",
    "Colesterol LDL",
    "Triglicerídeos",
    "Creatinina",
    "Ureia",
    "Ácido Úrico",
    "Sódio",
    "Potássio",
    "Cálcio Total",
    "Magnésio",
    "Ferro Sérico",
    "Ferritina",
    "Vitamina B12",
    "Vitamina D",
    "TSH",
    "T4 Livre",
    "T3 Total",
    "AST",
    "ALT",
    "Gama GT",
    "Fosfatase Alcalina",
    "Bilirrubina Total",
    "Bilirrubina Direta",
    "Proteína C Reativa",
    "VHS",
    "Albumina",
    "Proteínas Totais",
    "Amilase",
    "Lipase",
    "Insulina",
    "Cortisol",
    "Prolactina",
    "Testosterona Total",
    "Estradiol",
    "FSH",
    "LH",
    "PSA Total",
    "CEA",
    "Alfa Fetoproteína",
    "CA 125",
    "CA 19-9",
    "HIV 1 e 2",
    "HBsAg",
    "Anti-HBs",
    "Anti-HCV",
    "VDRL",
    "Toxoplasmose IgG",
    "Toxoplasmose IgM",
    "Rubéola IgG",
    "Rubéola IgM",
    "Citomegalovírus IgG",
    "Citomegalovírus IgM",
    "EAS",
    "Urocultura",
    "Parasitológico de Fezes",
    "Sangue Oculto nas Fezes",
]


def build_exams() -> list[dict[str, str]]:
    exams: list[dict[str, str]] = []

    for index, name in enumerate(
        COMMON_EXAMS,
        start=1,
    ):
        exams.append(
            {
                "name": name,
                "code": f"LAB{index:03d}",
            }
        )

    next_index = len(exams) + 1

    while len(exams) < 120:
        number = len(exams) + 1

        exams.append(
            {
                "name": (
                    f"Marcador Laboratorial "
                    f"Fictício {number:03d}"
                ),
                "code": f"LAB{next_index:03d}",
            }
        )

        next_index += 1

    return exams


def main() -> None:
    exams = build_exams()

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            exams,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Generated {len(exams)} exams "
        f"at {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()