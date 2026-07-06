# Аудит: Аудит интерфейса, пользовательского опыта и брендинга

**Роль:** UI/UX Designer
**Дата:** 2026-07-06 11:18
**Источники:** 3 файлов проанализировано

---

## Ключевые находки

1. Tabbed layout: 9 tabs ✓
2. Sidebar: ✓
3. Input methods: text_input=✓, file_upload=✓
4. CSV export: ✓
5. Metrics display (st.metric): ✓
6. Expandable sections: ✓
7. Data preview: ✓
8. Loading indicators: ✓
9. Error handling: ✓
10. Success feedback: ✓
11. Input placeholders: ✓
12. Validation flow: ✓
13. Batch processing: ✓
14. User journey: Single molecule → Batch → Validation — логичный прогресс
15. Charts/plots: ✗ — добавить визуализацию распределений
16. JSON export: ✓
17. Radio buttons: ✓
18. Action buttons: ✓
19. Брендинг: отсутствует — дефолтный Streamlit, нет логотипа, favicon, кастомного CSS
20. Название: 'ADME/Tox Predictor v2.0' — функционально, но не для маркетинга РФ
21. Цветовая схема: дефолтная Streamlit — не адаптирована под российскую аудиторию
22. Рекомендация по названию для РФ: 'ADMETox.AI' или 'Скрининг ADME/Tox'
23. Wide mode: ✗
24. Responsive tables: ✓

## Рекомендации

1. **Добавить визуализацию результатов: radar chart для сравнения молекул по 3+ свойствам**
2. **Добавить scaffold viewer (молекулярную структуру) через RDKit + Streamlit или st.image**
3. **Внедрить color-coding результатов (зелёный/жёлтый/красный) для быстрой оценки**
4. **Добавить onboarding для новых пользователей: tooltips, примеры SMILES, quick guide**
5. **Разработать брендинг: логотип, цветовая схема, favicon**
6. **Создать лендинг на русском с CJM: от входа до оплаты enterprise-лицензии**
7. **Добавить dark theme для Streamlit (через config или сторонний компонент)**
8. **Провести usability testing с 3-5 CRO-специалистами перед запуском в РФ**
