#!/usr/bin/env python3
"""
RISC-V Page Table Generator
Supports Sv39, Sv48, Sv57.
Supports multiple satp/hgatp values per stage via page_tables: list.
Supports 2-stage (H-extension) via stage1/stage2 config sections.

Usage:
    python3 pt_gen.py config.yaml [-o output.inc]

Requires: pyyaml  (pip install pyyaml)
"""

import argparse
import sys
import yaml

# ---------------------------------------------------------------------------
# Mode table
# ---------------------------------------------------------------------------

MODES = {
    'sv39': {'levels': 3, 'va_bits': 39, 'satp_mode': 8},
    'sv48': {'levels': 4, 'va_bits': 48, 'satp_mode': 9},
    'sv57': {'levels': 5, 'va_bits': 57, 'satp_mode': 10},
}

PAGE_SHIFT     = 12
PAGE_SIZE      = 1 << PAGE_SHIFT   # 4096
VPN_BITS       = 9
VPN_MASK       = (1 << VPN_BITS) - 1
PTES_PER_TABLE = 512

# G-stage (second stage) root table is 16KB — 4 pages / 2048 entries.
# The top-level VPN is 11 bits wide (9 normal + 2 extra for the x4 address extension).
G_STAGE_ROOT_PAGES = 4
G_STAGE_VPN_BITS   = 11
G_STAGE_VPN_MASK   = (1 << G_STAGE_VPN_BITS) - 1   # 0x7FF

# ---------------------------------------------------------------------------
# Default PTE attributes (read-write data page, not executable, not user)
# ---------------------------------------------------------------------------

DEFAULT_ATTRS = {'v': 1, 'r': 1, 'w': 1, 'x': 0, 'u': 0, 'g': 0, 'a': 1, 'd': 1}

# ---------------------------------------------------------------------------
# Size parsing
# ---------------------------------------------------------------------------

SIZE_UNITS = {'KB': 1 << 10, 'MB': 1 << 20, 'GB': 1 << 30, 'TB': 1 << 40}

def parse_size(s):
    """Parse '4KB', '2MB', '1GB', decimal, or hex string to bytes."""
    s = str(s).strip()
    su = s.upper()
    for unit, mult in SIZE_UNITS.items():
        if su.endswith(unit):
            return int(su[:-len(unit)]) * mult
    return int(s, 0)

def parse_int(v):
    """Parse decimal or hex integer (YAML may give us int or string)."""
    return int(str(v), 0)

def level_page_size(level):
    """Page size when a leaf PTE is placed at this level (level 0 = 4KB)."""
    return PAGE_SIZE << (VPN_BITS * level)

# ---------------------------------------------------------------------------
# PTE encoding
# ---------------------------------------------------------------------------

def make_leaf_pte(pa, attrs):
    a = attrs
    return (
        ((pa >> PAGE_SHIFT) << 10) |
        (a.get('d', 1) << 7) |
        (a.get('a', 1) << 6) |
        (a.get('g', 0) << 5) |
        (a.get('u', 0) << 4) |
        (a.get('x', 0) << 3) |
        (a.get('w', 1) << 2) |
        (a.get('r', 1) << 1) |
         a.get('v', 1)
    )

def make_pointer_pte(child_pa):
    """Non-leaf PTE: points to next-level table. V=1, R=W=X=0."""
    return ((child_pa >> PAGE_SHIFT) << 10) | 0x1

def satp_value(mode, asid, root_pa):
    m = MODES[mode]['satp_mode']
    return (m << 60) | ((asid & 0xFFFF) << 44) | (root_pa >> PAGE_SHIFT)

def decode_pte(pte):
    """One-line human-readable summary for .inc file comments."""
    if pte == 0:
        return 'empty'
    bits  = [(pte >> i) & 1 for i in range(8)]   # V R W X U G A D
    names = 'VRWXUGAD'
    flags = ''.join(n if b else '-' for n, b in zip(names, bits))
    ppn   = (pte >> 10) << PAGE_SHIFT
    kind  = 'leaf' if (bits[1] or bits[2] or bits[3]) else 'ptr '
    return f"{kind} PA={ppn:#011x} [{flags}]"

# ---------------------------------------------------------------------------
# PageTable — one stage, one satp/hgatp value
# ---------------------------------------------------------------------------

class PageTable:
    """
    Builds a RISC-V page table for one address-translation stage.

    Usage:
        pt = PageTable('sv39', base_pa=0x80010000)
        pt.add_mapping(va, pa, size, page_size, attrs)
        # pt.tables: dict PA -> list of PTEs  (ready to emit)
    """

    def __init__(self, mode, base_pa, g_stage=False):
        if mode not in MODES:
            raise ValueError(f"Unknown mode '{mode}'. Valid: {sorted(MODES)}")
        self.mode    = mode
        self.levels  = MODES[mode]['levels']
        self.g_stage = g_stage
        self.root_pa = base_pa
        self.tables  = {}        # PA -> list of PTEs (512 for normal, 2048 for G-stage root)
        self._next   = base_pa
        if g_stage:
            root_align = G_STAGE_ROOT_PAGES * PAGE_SIZE   # 16KB
            if base_pa % root_align:
                raise ValueError(
                    f"G-stage base_pa {base_pa:#x} must be 16KB-aligned "
                    f"(multiple of {root_align:#x})"
                )
        self._alloc_root()

    # -- internal helpers --

    def _alloc_root(self):
        """Allocate the root table: 16KB (2048 entries) for G-stage, 4KB (512) otherwise."""
        pa    = self._next
        n     = G_STAGE_ROOT_PAGES * PTES_PER_TABLE if self.g_stage else PTES_PER_TABLE
        pages = G_STAGE_ROOT_PAGES                  if self.g_stage else 1
        self.tables[pa] = [0] * n
        self._next += PAGE_SIZE * pages
        return pa

    def _alloc(self):
        """Allocate one fresh 4KB child page table, return its PA."""
        pa = self._next
        self.tables[pa] = [0] * PTES_PER_TABLE
        self._next += PAGE_SIZE
        return pa

    def _vpn(self, va, level):
        """Extract the VPN index for a given level from a VA.
        G-stage root level uses an 11-bit index (Svxx x4 extension)."""
        if self.g_stage and level == self.levels - 1:
            return (va >> (PAGE_SHIFT + VPN_BITS * level)) & G_STAGE_VPN_MASK
        return (va >> (PAGE_SHIFT + VPN_BITS * level)) & VPN_MASK

    def _page_size_to_level(self, page_size):
        for level in range(self.levels):
            if level_page_size(level) == page_size:
                return level
        valid = {level_page_size(l) for l in range(self.levels)}
        raise ValueError(
            f"page_size {page_size:#x} not valid for {self.mode}. "
            f"Valid sizes: {sorted(hex(s) for s in valid)}"
        )

    # -- public API --

    def add_mapping(self, va, pa, size, page_size=PAGE_SIZE, attrs=None):
        """
        Map the region [va, va+size) -> [pa, pa+size).
        page_size controls the leaf granularity (4KB / 2MB / 1GB / ...).
        attrs overrides individual DEFAULT_ATTRS fields.
        """
        effective  = {**DEFAULT_ATTRS, **(attrs or {})}
        leaf_level = self._page_size_to_level(page_size)
        gran       = level_page_size(leaf_level)

        if va % gran:
            raise ValueError(f"VA {va:#x} not aligned to page_size {gran:#x}")
        if pa % gran:
            raise ValueError(f"PA {pa:#x} not aligned to page_size {gran:#x}")
        if size % gran:
            raise ValueError(f"size {size:#x} not a multiple of page_size {gran:#x}")

        for offset in range(0, size, gran):
            self._map_one(va + offset, pa + offset, leaf_level, effective)

    def _map_one(self, va, pa, leaf_level, attrs):
        """Walk/build the tree for one page and install the leaf PTE."""
        table_pa = self.root_pa

        # Walk from root down to the level just above leaf_level
        for level in range(self.levels - 1, leaf_level, -1):
            vpn   = self._vpn(va, level)
            table = self.tables[table_pa]
            if table[vpn] == 0:
                child_pa   = self._alloc()
                table[vpn] = make_pointer_pte(child_pa)
            else:
                existing = table[vpn]
                # If the existing entry is a leaf, this VA overlaps an existing huge-page mapping
                if existing & 0xE:  # R|W|X != 0 → leaf
                    gran = level_page_size(level)
                    raise ValueError(
                        f"VA {va:#x} conflicts with an existing {gran // (1<<20)}MB "
                        f"huge-page mapping at level {level}"
                    )
                child_pa = (existing >> 10) << PAGE_SHIFT
            table_pa = child_pa

        # Install leaf PTE at leaf_level
        self.tables[table_pa][self._vpn(va, leaf_level)] = make_leaf_pte(pa, attrs)

# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def _add_mapping(pt, m):
    """Parse one mapping entry from YAML and call pt.add_mapping."""
    va        = parse_int(m['va'])
    pa_raw    = m['pa']
    pa        = va if str(pa_raw).strip().lower() == 'same' else parse_int(pa_raw)
    size      = parse_size(m['size'])
    page_size = parse_size(m.get('page_size', '4KB'))
    attrs     = {k: int(v) for k, v in m.get('attrs', {}).items()}
    pt.add_mapping(va, pa, size, page_size, attrs)

def _load_pt_entry(pt_cfg, default_mode, default_label, g_stage):
    """Build one PageTable from a single entry config dict."""
    mode    = pt_cfg.get('mode', default_mode)
    label   = pt_cfg.get('label', default_label)
    base_pa = parse_int(pt_cfg['base_pa'])
    asid    = parse_int(pt_cfg.get('asid', 0))
    pt      = PageTable(mode, base_pa, g_stage=g_stage)
    for m in pt_cfg.get('mappings', []):
        _add_mapping(pt, m)
    return {'label': label, 'mode': mode, 'asid': asid, 'pt': pt}

def load_stage_group(cfg, default_label, g_stage=False):
    """
    Load one stage group (VS or G) from config.
    Supports both old single-table format and new page_tables: list format.
    Returns {'g_stage': bool, 'pt_entries': [{'label', 'mode', 'asid', 'pt'}, ...]}
    """
    default_mode = cfg.get('mode', 'sv39')

    if 'page_tables' in cfg:
        entries = [
            _load_pt_entry(pt_cfg, default_mode,
                           pt_cfg.get('label', f"{default_label}_{i}"), g_stage)
            for i, pt_cfg in enumerate(cfg['page_tables'])
        ]
    else:
        entries = [_load_pt_entry(cfg, default_mode, default_label, g_stage)]

    return {'g_stage': g_stage, 'pt_entries': entries}

def load_config(path):
    with open(path) as f:
        cfg = yaml.safe_load(f)

    if 'stage1' in cfg or 'stage2' in cfg:
        groups = []
        if 'stage1' in cfg:
            groups.append(load_stage_group(cfg['stage1'], 'vs', g_stage=False))
        if 'stage2' in cfg:
            groups.append(load_stage_group(cfg['stage2'], 'g',  g_stage=True))
        return groups

    return [load_stage_group(cfg, 'pt', g_stage=False)]

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _emit_page(out, name, pa, ptes):
    """Emit one 512-entry page table page."""
    out.write(f"    .align 12\n")
    out.write(f"{name}:  # PA {pa:#018x}\n")
    i = 0
    while i < PTES_PER_TABLE:
        if ptes[i] == 0:
            j = i + 1
            while j < PTES_PER_TABLE and ptes[j] == 0:
                j += 1
            out.write(f"    .fill {j - i}, 8, 0  # [{i}..{j-1}] empty\n")
            i = j
        else:
            out.write(f"    .dword {ptes[i]:#018x}  # [{i}] {decode_pte(ptes[i])}\n")
            i += 1
    out.write("\n")

def emit_table(out, name, pa, ptes):
    """Emit a page table node. G-stage root (2048 entries) is split into 4 pages."""
    if len(ptes) == G_STAGE_ROOT_PAGES * PTES_PER_TABLE:
        for p in range(G_STAGE_ROOT_PAGES):
            chunk = ptes[p * PTES_PER_TABLE : (p + 1) * PTES_PER_TABLE]
            _emit_page(out, f"{name}_p{p}", pa + p * PAGE_SIZE, chunk)
    else:
        _emit_page(out, name, pa, ptes)

def emit_inc(stage_groups, out):
    out.write("# Generated by pt_gen.py — do not edit\n\n")
    out.write("    .section .page_tables, \"aw\"\n\n")

    for sg in stage_groups:
        g_stage = sg['g_stage']
        for entry in sg['pt_entries']:
            label = entry['label']
            mode  = entry['mode']
            asid  = entry['asid']
            pt    = entry['pt']
            satp  = satp_value(mode, asid, pt.root_pa)
            csr   = 'hgatp' if g_stage else 'satp'

            out.write(f"# {'=' * 62}\n")
            out.write(f"# Label  : {label}\n")
            out.write(f"# Mode   : {mode}{'x4' if g_stage else ''}\n")
            out.write(f"# Root PA: {pt.root_pa:#018x}{'  (16KB-aligned)' if g_stage else ''}\n")
            out.write(f"# {csr.upper():<6} : {satp:#018x}  (load into {csr} CSR)\n")
            out.write(f"# Tables : {len(pt.tables)}\n")
            out.write(f"# {'=' * 62}\n\n")

            for i, (pa, ptes) in enumerate(sorted(pt.tables.items())):
                name = f"{label}_root" if pa == pt.root_pa else f"{label}_pt_{i}"
                emit_table(out, name, pa, ptes)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description='RISC-V page table generator')
    ap.add_argument('config', help='YAML config file')
    ap.add_argument('-o', '--output', default='-',
                    help='Output .inc file (default: stdout)')
    args = ap.parse_args()

    stage_groups = load_config(args.config)

    if args.output == '-':
        emit_inc(stage_groups, sys.stdout)
    else:
        with open(args.output, 'w') as f:
            emit_inc(stage_groups, f)
        print(f"Written: {args.output}", file=sys.stderr)

if __name__ == '__main__':
    main()
