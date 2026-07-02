import joblib
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Singleton service to load and manage the ML model artifact.
    Ensures the model is loaded only once at application startup.
    """
    _instance = None
    _model: Optional[Any] = None
    _model_metadata: Optional[dict] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance

    def load_model(self, model_path: str = "ml/artifacts/best_model.joblib"):
        path = Path(model_path)
        # Check parent directories or absolute path if not found (for monorepo structure)
        if not path.exists():
            # Try ascending one directory for local dev
            path = Path("../") / model_path
            
        if path.exists():
            try:
                self._model = joblib.load(path)
                logger.info(f"Model loaded successfully from {path}")
                self._model_metadata = {"status": "loaded", "path": str(path)}
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                self._model = None
                self._model_metadata = {"status": "error", "error": str(e)}
        else:
            logger.warning(f"Model file not found at {path}. Prediction endpoints will be disabled.")
            self._model_metadata = {"status": "not_found", "path": str(path)}

    def get_model(self) -> Optional[Any]:
        return self._model

    def get_info(self) -> dict:
        return self._model_metadata or {"status": "uninitialized"}

model_manager = ModelManager()
