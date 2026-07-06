from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
TEAM_DIR = BASE_DIR / "team"
OUTPUT_DIR = BASE_DIR / "team_output"
AUDIT_DIR = OUTPUT_DIR / "audit"
STRATEGY_DIR = OUTPUT_DIR / "strategy"
ROADMAP_DIR = OUTPUT_DIR / "roadmap"

ARTIFACTS = {
    "src": {
        "config": BASE_DIR / "src" / "config.py",
        "features": BASE_DIR / "src" / "features.py",
        "models": BASE_DIR / "src" / "models.py",
        "predict": BASE_DIR / "src" / "predict.py",
        "data_loader": BASE_DIR / "src" / "data_loader.py",
        "train": BASE_DIR / "src" / "train.py",
    },
    "app": BASE_DIR / "app.py",
    "training_results": BASE_DIR / "models" / "training_results.json",
    "session_resume": BASE_DIR / "SESSION_RESUME.md",
}

RUSSIAN_PHARMA_COMPANIES = [
    {"name": "BIOCAD", "type": "pharma", "focus": "oncology, immunology", "revenue": "~$1B", "size": "3,000+", "city": "SPb"},
    {"name": "R-Pharm", "type": "pharma", "focus": "hospital, oncology", "revenue": "~$1.5B", "size": "4,000+", "city": "Moscow"},
    {"name": "Geropharm", "type": "pharma", "focus": "diabetes, CNS", "size": "1,000+", "city": "SPb"},
    {"name": "Pharmasyntez", "type": "pharma", "focus": "oncology, HIV", "revenue": "~$200M", "city": "Irkutsk"},
    {"name": "ChemRar", "type": "CRO/pharma", "focus": "drug discovery, R&D", "size": "500+", "city": "Moscow"},
    {"name": "Khimrar", "type": "CRO", "focus": "custom synthesis, medicinal chemistry", "city": "Moscow"},
    {"name": "Pharmaprojects", "type": "research", "focus": "pharma market analytics, CRO registry", "city": "Moscow"},
    {"name": "Valenta Pharm", "type": "pharma", "focus": "OTC, generics", "revenue": "~$300M", "city": "Moscow"},
    {"name": "Otisifarm", "type": "pharma", "focus": "generics, pediatrics", "city": "Moscow"},
    {"name": "Akrikhin", "type": "pharma", "focus": "generics, branded generics", "revenue": "~$400M", "city": "Moscow region"},
    {"name": "Vertex", "type": "pharma", "focus": "generics, OTC", "revenue": "~$200M", "city": "SPb"},
    {"name": "Nizhpharm (Stada)", "type": "pharma", "focus": "generics, OTC", "city": "Nizhny Novgorod"},
    {"name": "Sotex", "type": "pharma", "focus": "infusions, cardiovascular", "city": "Moscow region"},
    {"name": "Novo Nordisk Russia", "type": "pharma", "focus": "diabetes, obesity", "city": "Moscow"},
    {"name": "Pfizer Russia", "type": "pharma", "focus": "oncology, vaccines", "city": "Moscow"},
    {"name": "Sanofi Russia", "type": "pharma", "focus": "diabetes, rare diseases", "city": "Moscow"},
]

RUSSIAN_CRO_COMPANIES = [
    {"name": "ChemRar", "type": "CRO", "focus": "hit ID, lead optimization, medicinal chemistry", "city": "Moscow"},
    {"name": "Khimrar", "type": "CRO", "focus": "custom synthesis, library design", "city": "Moscow"},
    {"name": "PharmChem", "type": "CRO", "focus": "ADME assays, in vitro screening", "city": "Moscow"},
    {"name": "Novoteh", "type": "CRO", "focus": "preclinical studies, toxicology", "city": "Moscow region"},
    {"name": "CRO Renovation", "type": "CRO", "focus": "clinical trials, regulatory", "city": "SPb"},
    {"name": "RML-CRO", "type": "CRO", "focus": "preclinical, analytical", "city": "Moscow"},
    {"name": "BioPharmExpert", "type": "CRO", "focus": "regulatory, CMC, preclinical", "city": "Moscow"},
    {"name": "NPO Farmanaliz", "type": "CRO", "focus": "analytical chemistry, quality control", "city": "Moscow"},
]

RUSSIAN_GRANTS = [
    {
        "program": "Старт-1", "org": "Фонд содействия инновациям (Фонд Бортника)",
        "amount": "до 4 млн руб", "type": "grant", "stage": "early",
        "focus": "НИОКР, прототип, проведение испытаний",
        "deadline": "2-3 цикла в год", "url": "https://fasie.ru/programs/programma-start/",
        "notes": "Безвозвратное финансирование, 70% на НИОКР"
    },
    {
        "program": "Старт-2", "org": "Фонд содействия инновациям",
        "amount": "до 15 млн руб", "type": "grant", "stage": "early",
        "focus": "коммерциализация, выпуск опытной партии",
        "deadline": "2-3 цикла в год", "url": "https://fasie.ru/programs/programma-start/",
    },
    {
        "program": "Сколково (участник)", "org": "Фонд Сколково",
        "amount": "льготы + гранты до 30 млн руб", "type": "grant + tax benefits", "stage": "early-mid",
        "focus": "получение статуса участника стартапа, компенсация R&D",
        "deadline": "постоянно", "url": "https://sk.ru/",
        "notes": "Ставка налога на прибыль 0%, страховые взносы 14%, гранты на НИОКР до 30 млн"
    },
    {
        "program": "РНФ (молодежные)", "org": "Российский научный фонд",
        "amount": "до 7 млн руб/год", "type": "grant", "stage": "research",
        "focus": "фундаментальные и поисковые исследования",
        "deadline": "ежегодно", "url": "https://rscf.ru/",
    },
    {
        "program": "РФРИТ", "org": "Российский фонд развития информационных технологий",
        "amount": "до 300 млн руб", "type": "subsidy", "stage": "growth",
        "focus": "AI и ПО, импортозамещение",
        "deadline": "по заявочным кампаниям", "url": "https://rfrit.ru/",
        "notes": "Требует 50% софинансирования"
    },
    {
        "program": "Коммерциализация", "org": "Фонд содействия инновациям",
        "amount": "до 30 млн руб", "type": "grant", "stage": "mid",
        "focus": "расширение производства, масштабирование",
        "deadline": "2-3 цикла в год", "url": "https://fasie.ru/programs/programma-kommercializaciya/",
    },
    {
        "program": "ИИ-стартапы", "org": "Минэкономразвития + Сбер",
        "amount": "до 50 млн руб", "type": "grant", "stage": "early-mid",
        "focus": "AI-first продукты, внедрение AI в промышленности",
        "deadline": "по кампаниям", "url": "https://ai.gov.ru/",
    },
]

AI_RUSSIAN_COMPETITORS = [
    {"name": "Insilico Medicine Russia", "focus": "hit ID, target ID", "note": "глобальный конкурент, российский офис есть"},
    {"name": "BIOPTIC", "focus": "hit ID generation", "note": "наш комплемент, а не конкурент"},
    {"name": "Way2Drug (ОИВТ РАН)", "focus": "PASS, drug repurposing", "note": "онлайн-инструмент, не AI-native"},
    {"name": "MolInsight", "focus": "QSAR, ADME prediction", "note": "малоизвестный, академический"},
    {"name": "Syntelly", "focus": "retrosynthesis, drug design", "note": "израильский, но работает с РФ"},
    {"name": "CROC (биоинформатика)", "focus": "bioinformatics, genomics", "note": "CRO, а не AI"},
]

VCS_RUSSIAN = [
    {"name": "Kama Flow", "focus": "deep tech, biotech", "stage": "seed-series A", "check": "$0.5-5M"},
    {"name": "RBF Ventures", "focus": "bio/med tech", "stage": "pre-seed, seed", "check": "$0.1-1M"},
    {"name": "PharmMed Ventures", "focus": "pharma, med devices", "stage": "seed-growth", "check": "$0.5-3M"},
    {"name": "VEB Ventures", "focus": "deep tech, AI, pharma", "stage": "series A+", "check": "$1-10M"},
    {"name": "Sber Investments", "focus": "AI, healthcare", "stage": "growth", "check": "$5M+"},
    {"name": "Internet Initiatives Development Fund (IIDF)", "focus": "IT, AI", "stage": "seed", "check": "до ₽25M"},
]

PROPERTY_IMPORTANCE_RUSSIAN = {
    "solubility": {
        "importance": "critical",
        "reason_ru": "Регуляторные требования РФ (ГФ РФ) требуют определения растворимости для всех субстанций",
    },
    "caco2": {
        "importance": "high",
        "reason_ru": "Ключевой параметр для BCS-классификации (рекомендации МЗ РФ по биоэквивалентности)",
    },
    "herg": {
        "importance": "critical",
        "reason_ru": "Регуляторные требования (ICH S7B, приняты в РФ) обязательны для всех NCE",
    },
    "lipophilicity": {
        "importance": "high",
        "reason_ru": "CliP/LogP используется в РФ для ADME-профилирования на ранних стадиях",
    },
    "pgp": {
        "importance": "medium",
        "reason_ru": "Растет внимание МЗ РФ к drug-drug interactions",
    },
    "bioavailability": {
        "importance": "medium",
        "reason_ru": "F% предсказание — востребовано, но сложно без данных по метаболизму",
    },
}
