#!/usr/bin/env python3
"""Recria todos os diagramas a partir do spec: python3 harness/diagrams/build_all.py"""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# ordem: os filhos embutidos antes de quem os embute (não é obrigatório, só legível)
SCRIPTS = [
    "build_chip_warp.py", "build_chip_sm.py", "build_chip_floorplan.py",
    "build_chip_isa.py", "build_chip_risc.py", "build_chip_memhier.py",
    "build_sys_mmu.py", "build_sys_irq.py",
]

if __name__ == "__main__":
    found = sorted(p.name for p in HERE.glob("build_*.py") if p.name != "build_all.py")
    missing = sorted(set(found) - set(SCRIPTS))
    if missing:
        sys.exit(f"scripts fora da lista de build_all.py: {missing}")
    for name in SCRIPTS:
        runpy.run_path(str(HERE / name), run_name="__main__")
