"""Type-specific formatters."""

from __future__ import annotations

from typing import Any, Protocol

from ._base import get_module, truncate


class Formatter(Protocol):
    def supports(self, obj: Any) -> bool: ...
    def format(self, obj: Any, **opts: Any) -> dict[str, Any]: ...


class DFFormatter:
    def supports(self, obj: Any) -> bool:
        pd = get_module("pandas")
        return pd is not None and isinstance(obj, pd.DataFrame)

    def format(self, obj: Any, max_rows: int = 5, **_: Any) -> dict[str, Any]:
        return {
            "_type": "DataFrame",
            "shape": list(obj.shape),
            "columns": list(obj.columns)[:20],
            "dtypes": {str(k): str(v) for k, v in list(obj.dtypes.items())[:20]},
            "head": obj.head(max_rows).to_dict(orient="records"),
        }


class TensorFormatter:
    def supports(self, obj: Any) -> bool:
        return hasattr(obj, "shape") and hasattr(obj, "dtype")

    def format(self, obj: Any, **_: Any) -> dict[str, Any]:
        r: dict[str, Any] = {
            "_type": type(obj).__name__,
            "shape": list(getattr(obj.shape, "__iter__", lambda: [obj.shape])()),
            "dtype": str(obj.dtype),
        }
        try:
            r.update({"min": float(obj.min()), "max": float(obj.max()), "mean": float(obj.mean())})
            if hasattr(obj, "std"):
                r["std"] = float(obj.std())
            if hasattr(obj, "device"):
                r["device"] = str(obj.device)
        except:
            pass
        return r


class ImageFormatter:
    def supports(self, obj: Any) -> bool:
        PIL = get_module("PIL")
        return PIL is not None and hasattr(PIL, "Image") and isinstance(obj, PIL.Image.Image)

    def format(self, obj: Any, max_size: tuple[int, int] = (256, 256), **_: Any) -> dict[str, Any]:
        return {"_type": "Image", "size": list(obj.size), "mode": obj.mode}


# Combined formatter
_FMT: list[Formatter] = [DFFormatter(), TensorFormatter(), ImageFormatter()]


def format_value(obj: Any, **opts: Any) -> Any:
    for f in _FMT:
        if f.supports(obj):
            return f.format(obj, **opts)
    return truncate(obj, opts.get("max_depth", 3), opts.get("max_len", 500))
