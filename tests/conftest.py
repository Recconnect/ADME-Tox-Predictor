import warnings

warnings.filterwarnings("ignore", message="X does not have valid feature names")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="rdkit")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sklearn")
warnings.filterwarnings("ignore", ".*Setting the shape on a NumPy array.*")
warnings.filterwarnings("ignore", ".*asyncio.iscoroutinefunction.*")
warnings.filterwarnings("ignore", ".*Using.*httpx.*with.*starlette.*")
