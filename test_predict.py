import sys
sys.path.insert(0, '.')
from src.predict import ADMETPredictor

print('Creating predictor...')
predictor = ADMETPredictor()
print(f'Models loaded: {len(predictor.model_keys)}')
print(f'Model keys: {predictor.model_keys}')
print(f'Is ready: {predictor.is_ready}')

print('\nTesting prediction for CCO (ethanol)...')
result = predictor.predict_single('CCO')
if 'error' in result:
    print(f'Error: {result["error"]}')
else:
    print(f'SMILES: {result.get("SMILES", "N/A")}')
    print(f'Solubility: {result.get("Solubility (logS)", "N/A")}')
    print(f'Caco-2 Class: {result.get("Caco-2 Class", "N/A")}')
    print(f'hERG Class: {result.get("hERG Class", "N/A")}')
    print('Prediction successful!')
