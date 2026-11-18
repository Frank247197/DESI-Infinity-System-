# ============================================================
# DESI∞ INFINITY SYSTEM 6.2 - REST API SERVICE INTERFACE
# Structured Endpoint Routing, Input Validation & OpenAPI Spec
# ============================================================

from typing import Dict, Any, Callable

class DESIAPIRouter:
    """
    [CALC] Lightweight, framework-agnostic REST API service router exposing
    DESI-Infinity scientific endpoints with strict versioned schemas.
    """
    def __init__(self, api_version: str = "v1"):
        self.api_version = api_version
        self._routes: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}

    def route(self, path: str):
        full_path = f"/api/{self.api_version}{path}"
        def decorator(func: Callable[[Dict[str, Any]], Dict[str, Any]]):
            self._routes[full_path] = func
            return func
        return decorator

    def dispatch(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if path not in self._routes:
            return {"status_code": 404, "error": f"Endpoint '{path}' not found."}
        try:
            data = self._routes[path](payload)
            return {"status_code": 200, "api_version": self.api_version, "data": data}
        except Exception as e:
            return {"status_code": 400, "error": str(e)}

    def get_openapi_summary(self) -> Dict[str, Any]:
        return {
            "service": "DESI-Infinity Computational Ecosystem",
            "version": self.api_version,
            "endpoints": sorted(list(self._routes.keys()))
        }

api = DESIAPIRouter(api_version="v1")

@api.route("/health")
def health_check(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"system": "DESI-INFINITY-6.2", "status": "OPERATIONAL"}

@api.route("/genomics/gc-content")
def gc_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    seq = payload.get("sequence", "").upper()
    if not seq or any(base not in {"A", "T", "C", "G"} for base in seq):
        raise ValueError("Invalid DNA sequence provided.")
    gc = round(((seq.count("G") + seq.count("C")) / len(seq)) * 100.0, 2)
    return {"sequence_length": len(seq), "gc_percent": gc}

if __name__ == "__main__":
    print("OpenAPI Spec:", api.get_openapi_summary())
    print("Health Response:", api.dispatch("/api/v1/health", {}))
    print("GC Response:", api.dispatch("/api/v1/genomics/gc-content", {"sequence": "GCGCATAT"}))
