"""
CIRCOR International - IFS Cloud Medallion Lakehouse Pipeline
Processes shop floor execution, Heat Lot genealogy, and COS Lean metrics.
"""

from .circor_cos_pyspark_pipeline import calculate_cos_lean_kpis

__all__ = ["calculate_cos_lean_kpis"]
