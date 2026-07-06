# Аудит: Технический аудит: ML-архитектура, инфраструктура, performance

**Роль:** ML Engineer
**Дата:** 2026-07-06 11:18
**Источники:** 6 файлов проанализировано

---

## Ключевые находки

1. Регрессия (Solubility): LGBMRegressor ✓
2. Классификация (Caco-2, hERG): LGBMClassifier ✓
3. Early stopping: ✓
4. Feature importance: ✗ — добавить анализ важности
5. Cross-validation: ✗ — только scaffold split
6. Ансамбль из 3 моделей — адекватная архитектура для MVP
7. LRU caching: ✓
8. Batch processing: ✓
9. Chunking: ✓
10. Validation mode: ✓
11. Model persistence (joblib): ✓
12. Metadata in saved models: ✓
13. Feature dimension validation: ✓
14. Graceful error handling: ✓
15. Streamlit: ✓
16. Resource caching: ✓
17. Tabbed UI: ✓
18. CSV export: ✓
19. Export format: joblib
20. ONNX export: ✗ — добавить для production
21. MLflow tracking: ✗ — добавить для экспериментов

## Рекомендации

1. **Обновить LightGBM до последней версии и зафиксировать версии пакетов в requirements.txt**
2. **Добавить автоматический GridSearchCV или Optuna для подбора гиперпараметров**
3. **Внедрить мониторинг дрейфа данных (Data drift detection via Evidently AI или аналог)**
4. **Создать REST API на FastAPI с асинхронной обработкой для production B2B**
5. **Добавить тестирование на производительность (latency, throughput) в CI**
6. **Разработать Dockerfile + docker-compose для одношагового деплоя**
7. **Добавить feature store (feast или простой SQLite) для отслеживания фичей между версиями моделей**
8. **Исследовать GNN (PyTorch Geometric) для улучшения метрик на 5-10% в следующей итерации**
