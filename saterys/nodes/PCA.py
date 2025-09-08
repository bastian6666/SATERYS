# nodes/pca.py
"""
PCA node (per-pixel projection across bands).

- Inputs:
  * EITHER one multiband raster (bands = variables),
  * OR a stack of single-band rasters (same grid), treated as variables.

- Output:
  * Multi-band GeoTIFF with the first k principal components (PC1..PCk), each
    band a component score image.
  * Plots saved to disk:
      - Scree plot (explained variance ratio)
      - Loadings heatmap (components x variables)
    Paths to these PNGs are returned in payload["artifacts"].

No scikit-learn dependency; PCA via NumPy SVD.

Requirements: rasterio, numpy, matplotlib (for plots; optional—plots skipped if missing)
"""

from __future__ import annotations
import os, hashlib, math
from typing import Any, Dict, List, Tuple, Optional

NAME = "raster.pca"
DEFAULT_ARGS = {
    # Number of components. If 0 or None, choose smallest k reaching >= variance_threshold.
    "n_components": 0,
    "variance_threshold": 0.99,   # only used if n_components in (0,None)
    "standardize": True,          # center & scale by std; if False: center only
    "sample_fraction": 0.1,       # 0< f <=1 for computing PCA basis (for speed)
    "random_seed": 42,

    # Optional variable (band) names to label loadings
    "var_names": [],              # if empty, auto "B1","B2",...

    # Output
    "output_path": "",            # if empty: ./data/cache/pca-<hash>.tif
    "dtype": "float32",
    "nodata": -9999.0,

    # Plots
    "make_plots": True,
    "plots_dir": "./data/plots",  # directory to save PNGs
    "plot_prefix": "pca",         # filename prefix
}

# ---------------------------------------------------------------------------

def _cache_dir() -> str:
    return os.path.abspath(os.getenv("RASTER_CACHE", "./data/cache"))

def _ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def _first_nonstr_none(x, default):
    return x if x is not None else default

def _collect_upstream_rasters(inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for v in inputs.values():
        if isinstance(v, dict) and v.get("type") == "raster" and v.get("path"):
            out.append(v)
    return out

def _assert_same_grid(rasters: List[Dict[str, Any]]):
    if not rasters: return
    r0 = rasters[0]
    for r in rasters[1:]:
        if r.get("crs") != r0.get("crs"): raise ValueError("PCA: CRS mismatch among inputs")
        if r.get("transform") != r0.get("transform"): raise ValueError("PCA: transform mismatch among inputs")
        if r.get("width") != r0.get("width") or r.get("height") != r0.get("height"):
            raise ValueError("PCA: dimension mismatch among inputs")

def _auto_name(paths: Tuple[str, ...], nvar: int) -> str:
    h = hashlib.sha1(("|".join(paths) + f"|{nvar}").encode("utf-8")).hexdigest()[:16]
    return f"pca-{h}.tif"

# ---------------------------------------------------------------------------

def run(args: Dict[str, Any], inputs: Dict[str, Any], context: Dict[str, Any]):
    import numpy as np
    import rasterio

    rasters = _collect_upstream_rasters(inputs)
    if not rasters:
        raise ValueError("PCA: no upstream raster(s) found")

    # --- Determine variables & read handles ---
    # Case A: one multiband raster
    # Case B: stack of single-band rasters (treated as variables)
    single_multiband = False
    if len(rasters) == 1:
        single_multiband = True

    _assert_same_grid(rasters)

    # Open datasets
    dsets = [rasterio.open(r["path"]) for r in rasters]
    try:
        height = dsets[0].height
        width  = dsets[0].width
        crs    = dsets[0].crs
        transform = dsets[0].transform

        if single_multiband:
            nvar = dsets[0].count
            var_paths = (rasters[0]["path"],)
            # Read masks: valid where all bands are valid
            # We'll build accessors to read band i (1-based)
            def read_var(i):
                return dsets[0].read(i, masked=True).astype("float32")
            var_names = args.get("var_names") or [f"B{i}" for i in range(1, nvar+1)]
        else:
            # stack of single-band rasters as variables
            for ds in dsets:
                if ds.count != 1:
                    raise ValueError("PCA: stack mode expects single-band rasters as variables")
            nvar = len(dsets)
            var_paths = tuple(r["path"] for r in rasters)
            def read_var(i):
                return dsets[i-1].read(1, masked=True).astype("float32")
            var_names = args.get("var_names") or [f"V{i}" for i in range(1, nvar+1)]

        # --- Compute valid mask: where all variables finite ---
        vars_data = [read_var(i) for i in range(1, nvar+1)]
        # Combine mask; np.ma has mask True where invalid
        mask_any = None
        for arr in vars_data:
            mask_any = arr.mask if mask_any is None else (mask_any | arr.mask)
        valid_mask = ~mask_any  # True where valid

        # --- Compute valid mask: valid where ALL variables are finite AND unmasked ---
        vars_data = [read_var(i) for i in range(1, nvar+1)]
        import numpy as np

        valid_mask = np.ones((height, width), dtype=bool)
        for A in vars_data:
            # treat both mask and non-finite values as invalid
            finiteA = np.isfinite(A.filled(np.nan))
            valid_mask &= (~A.mask) & finiteA
            mA = np.ma.getmaskarray(A)               # always (H, W)
            valid_mask &= (~mA) & finiteA

        valid_idx = np.flatnonzero(valid_mask.ravel())
        if valid_idx.size == 0:
            raise ValueError("PCA: no valid pixels after masking non-finite values")

        # sampling
        rng = np.random.RandomState(int(args.get("random_seed", 42)))
        frac = float(args.get("sample_fraction", 0.1))
        frac = 1.0 if not (0.0 < frac <= 1.0) else frac
        ns = max(1, int(valid_idx.size * frac))
        sample_idx = rng.choice(valid_idx, size=ns, replace=False)

        # Build sample matrix and sanitize
        Xs = np.empty((sample_idx.size, nvar), dtype="float32")
        for j, A in enumerate(vars_data):
            v = A.filled(np.nan).ravel()[sample_idx]
            Xs[:, j] = v

        # Drop any rows with NaN/Inf (paranoid)
        finite_rows = np.all(np.isfinite(Xs), axis=1)
        Xs = Xs[finite_rows, :]
        if Xs.shape[0] == 0:
            # fallback: resample all valid pixels
            sample_idx = valid_idx
            Xs = np.empty((sample_idx.size, nvar), dtype="float32")
            for j, A in enumerate(vars_data):
                v = A.filled(np.nan).ravel()[sample_idx]
                Xs[:, j] = v
            finite_rows = np.all(np.isfinite(Xs), axis=1)
            Xs = Xs[finite_rows, :]
            if Xs.shape[0] == 0:
                raise ValueError("PCA: all valid locations contain non-finite values across variables")


        # Center/standardize
        standardize = bool(args.get("standardize", True))
        mean_ = np.nanmean(Xs, axis=0).astype("float32")
        std_  = np.nanstd (Xs, axis=0).astype("float32")
        std_[std_ == 0] = 1.0

        Xs0 = Xs - mean_[None, :]
        if standardize:
            Xs0 = Xs0 / std_[None, :]

        # PCA via SVD on sample
        # Xs0 = U S Vt ; columns of V (rows of Vt) are PCs (loadings)
        U, S, Vt = np.linalg.svd(Xs0, full_matrices=False)
        # explained variance
        n_samples = Xs0.shape[0]
        ev = (S ** 2) / max(1, (n_samples - 1))
        evr = ev / np.sum(ev)

        # decide number of components
        n_components = int(args.get("n_components") or 0)
        if n_components <= 0:
            thresh = float(args.get("variance_threshold", 0.99))
            cumulative = np.cumsum(evr)
            n_components = int(np.searchsorted(cumulative, thresh) + 1)
        n_components = max(1, min(n_components, nvar))

        # PCs to keep
        Vt_k = Vt[:n_components, :]   # (k, nvar)
        loadings = Vt_k.astype("float32")  # rows are components

        # --- Project FULL image into k components (chunked to save RAM) ---
        # For each variable, build centered/scaled array
        # We'll compute scores = (X - mean)/std @ V (vars x comps), respecting mask
        out_dtype = str(args.get("dtype", "float32")).lower()
        if out_dtype not in ("float32", "float64"):
            out_dtype = "float32"
        nodata_val = float(args.get("nodata", -9999.0))

        # Prepare output path
        out_path = (args.get("output_path") or "").strip()
        if not out_path:
            cache_root = _cache_dir()
            _ensure_dir(cache_root)
            out_path = os.path.join(cache_root, _auto_name(var_paths, nvar))
        else:
            _ensure_dir(os.path.dirname(os.path.abspath(out_path)))
        out_path = os.path.abspath(out_path)

        # Create output dataset
        profile = dsets[0].profile
        profile.update(
            driver="GTiff",
            height=height,
            width=width,
            count=n_components,
            dtype=out_dtype,
            crs=crs,
            transform=transform,
            nodata=nodata_val,
            compress="deflate",
            tiled=True,
            blockxsize=min(512, width),
            blockysize=min(512, height),
        )

        with rasterio.open(out_path, "w", **profile) as dst:
            # Process by windows/blocks
            # We'll iterate in chunks of rows to keep memory in check
            rows_per_chunk = max(64, min(height, 512))
            for row0 in range(0, height, rows_per_chunk):
                row1 = min(height, row0 + rows_per_chunk)
                h = row1 - row0
                # read window for all variables
                Xwin = np.empty((h * width, nvar), dtype="float32")
                valid_win = None
                for j, A in enumerate(vars_data):
                    win = np.ma.array(A[row0:row1, :], copy=False)
                    m = np.ma.getmaskarray(win)              # shape (h, width)

                    if valid_win is None:
                        valid_win = ~m                       # shape (h, width)
                    else:
                        valid_win &= ~m

                    Xwin[:, j] = win.filled(np.nan).reshape(-1)

                # standardize window
                Xwin -= mean_[None, :]
                if standardize:
                    Xwin /= std_[None, :]

                # compute scores only where valid across all variables
                vflat = valid_win.reshape(-1)
                scores = np.full((h * width, n_components), np.nan, dtype="float32")
                if np.any(vflat):
                    Xv = Xwin[vflat, :]   # (nv, nvar)
                    Sv = np.dot(Xv, loadings.T)  # (nv, k)
                    scores[vflat, :] = Sv.astype("float32")

                # write each component band, filling nodata where NaN
                for k in range(n_components):
                    band = scores[:, k].reshape(h, width)
                    band = np.where(np.isfinite(band), band, nodata_val).astype(out_dtype)
                    dst.write(band, k + 1)
                    if row0 == 0:
                        dst.set_band_description(k + 1, f"PC{k+1}")

        # --- Save plots to disk (optional) ---
        artifacts: List[str] = []
        make_plots = bool(args.get("make_plots", True))
        if make_plots:
            try:
                import matplotlib
                matplotlib.use("Agg")
                import matplotlib.pyplot as plt  # type: ignore

                plots_dir = os.path.abspath(args.get("plots_dir") or "./data/plots")
                _ensure_dir(plots_dir)
                prefix = str(args.get("plot_prefix") or "pca")

                # Scree plot
                scree_path = os.path.join(plots_dir, f"{prefix}-scree.png")
                fig, ax = plt.subplots(figsize=(5.2, 3.2), dpi=120)
                ax.plot(range(1, len(evr) + 1), evr, marker="o")
                ax.set_title("PCA Scree (explained variance ratio)")
                ax.set_xlabel("Component")
                ax.set_ylabel("Explained variance ratio")
                ax.grid(True, alpha=0.3)
                fig.tight_layout()
                fig.savefig(scree_path)
                plt.close(fig)
                artifacts.append(scree_path)

                # Loadings heatmap (k x nvar)
                load_path = os.path.join(plots_dir, f"{prefix}-loadings.png")
                fig, ax = plt.subplots(figsize=(max(4.0, 0.5 * nvar), max(3.0, 0.5 * n_components)), dpi=120)
                im = ax.imshow(loadings, aspect="auto", cmap="coolwarm", vmin=-1, vmax=1)
                ax.set_title("PCA Loadings")
                ax.set_xlabel("Variables")
                ax.set_ylabel("Components")
                ax.set_xticks(range(nvar))
                ax.set_xticklabels(var_names, rotation=45, ha="right", fontsize=8)
                ax.set_yticks(range(n_components))
                ax.set_yticklabels([f"PC{i+1}" for i in range(n_components)])
                fig.colorbar(im, ax=ax, orientation="vertical", label="loading")
                fig.tight_layout()
                fig.savefig(load_path)
                plt.close(fig)
                artifacts.append(load_path)
            except Exception:
                # If matplotlib is missing or fails, skip plots silently
                pass

        # --- Return payload ---
        payload: Dict[str, Any] = {
            "type": "raster",
            "driver": "GTiff",
            "path": out_path,
            "width": int(width),
            "height": int(height),
            "count": int(n_components),
            "dtype": str(profile["dtype"]),
            "crs": str(crs) if crs else None,
            "transform": [transform.a, transform.b, transform.c,
                          transform.d, transform.e, transform.f],
            "bounds": [float(dsets[0].bounds.left), float(dsets[0].bounds.bottom),
                       float(dsets[0].bounds.right), float(dsets[0].bounds.top)],
            "nodata": float(profile.get("nodata")) if profile.get("nodata") is not None else None,
            "band_names": [f"PC{i+1}" for i in range(n_components)],
            "meta": {
                "source": "pca",
                "mode": "multiband" if single_multiband else "stack",
                "inputs": [os.path.abspath(p) for p in var_paths] if isinstance(var_paths, tuple) else [os.path.abspath(p) for p in var_paths],
                "n_variables": int(nvar),
                "n_components": int(n_components),
                "standardize": bool(args.get("standardize", True)),
                "explained_variance": [float(x) for x in ev[:n_components].tolist()],
                "explained_variance_ratio": [float(x) for x in evr[:n_components].tolist()],
                "var_names": [str(v) for v in var_names],
            },
        }
        if make_plots and 'artifacts' not in payload:
            payload["artifacts"] = artifacts  # list of PNG paths (if created)

        return payload

    finally:
        for ds in dsets:
            try:
                ds.close()
            except Exception:
                pass
