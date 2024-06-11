"""Optional ONNX import."""

from baybe.exceptions import OptionalImportError

try:
    import onnxruntime  # noqa: F401
except ModuleNotFoundError as ex:
    raise OptionalImportError(
        "Custom surrogate models are unavailable because 'onnxruntime' is not "
        "installed. "
        "Consider installing BayBE with 'onnx' dependency, "
        "e.g. via `pip install baybe[onnx]`."
    ) from ex
