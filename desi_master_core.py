# ============================================================
# DESI∞ INFINITY SYSTEM 6.0 - ADVANCED MASTER CORE
# Backward-compatible research and computational platform
# Standard library only | Educational/research use
# ============================================================
"""
DESI∞ INFINITY SYSTEM 6.0

Compatibility:
- Retains Version 5.0 public names and core behaviour:
  validate_dna, validate_rna, calculate_gc_content,
  simulate_crispr_mutation, transcribe_dna_to_mrna, translate_mrna,
  transcribe_and_translate, compare_translations, SignalWindow,
  SignalReport, validate_window, summarize_signal, process_window,
  MutationResult, TranslationResult, TranslationComparison,
  CODON_TABLE, main.

Safety:
- Mutation functions perform string-level simulations only. They do not
  design, guide, or perform biological editing.
- Cardiac/neural functions perform signal-quality checks and descriptive
  computation only. They do not diagnose or recommend treatment.
- Imaging functions process numerical pixel matrices; no medical diagnosis.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from hashlib import sha256
from logging import getLogger, NullHandler, basicConfig, INFO
from math import isfinite, cos, sin
from pathlib import Path
from statistics import mean, median, pstdev
from time import time
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple
import json
import unittest


# ---------------------- MODULE METADATA -----------------------

MODULE_NAME = "DESI∞ INFINITY SYSTEM 6.0 - ADVANCED MASTER CORE"
MODULE_VERSION = "6.0"
COMPATIBILITY_VERSION = "5.0"

DNA_BASES = frozenset("ATCG")
RNA_BASES = frozenset("AUCG")
STOP_CODONS = frozenset({"UAA", "UAG", "UGA"})
logger = getLogger("DESI.MASTERCORE")
logger.addHandler(NullHandler())


# ---------------------- STANDARD GENETIC CODE -----------------

CODON_TABLE: Dict[str, str] = {
    "UUU": "Phenylalanine", "UUC": "Phenylalanine",
    "UUA": "Leucine", "UUG": "Leucine",
    "CUU": "Leucine", "CUC": "Leucine",
    "CUA": "Leucine", "CUG": "Leucine",
    "AUU": "Isoleucine", "AUC": "Isoleucine",
    "AUA": "Isoleucine", "AUG": "Methionine",
    "GUU": "Valine", "GUC": "Valine",
    "GUA": "Valine", "GUG": "Valine",
    "UCU": "Serine", "UCC": "Serine",
    "UCA": "Serine", "UCG": "Serine",
    "AGU": "Serine", "AGC": "Serine",
    "CCU": "Proline", "CCC": "Proline",
    "CCA": "Proline", "CCG": "Proline",
    "ACU": "Threonine", "ACC": "Threonine",
    "ACA": "Threonine", "ACG": "Threonine",
    "GCU": "Alanine", "GCC": "Alanine",
    "GCA": "Alanine", "GCG": "Alanine",
    "UAU": "Tyrosine", "UAC": "Tyrosine",
    "UAA": "STOP", "UAG": "STOP", "UGA": "STOP",
    "CAU": "Histidine", "CAC": "Histidine",
    "CAA": "Glutamine", "CAG": "Glutamine",
    "AAU": "Asparagine", "AAC": "Asparagine",
    "AAA": "Lysine", "AAG": "Lysine",
    "GAU": "Aspartic Acid", "GAC": "Aspartic Acid",
    "GAA": "Glutamic Acid", "GAG": "Glutamic Acid",
    "UGU": "Cysteine", "UGC": "Cysteine",
    "UGG": "Tryptophan",
    "CGU": "Arginine", "CGC": "Arginine",
    "CGA": "Arginine", "CGG": "Arginine",
    "AGA": "Arginine", "AGG": "Arginine",
    "GGU": "Glycine", "GGC": "Glycine",
    "GGA": "Glycine", "GGG": "Glycine",
}


# ============================================================
# SHARED ERROR TYPES AND VALIDATION
# ============================================================

class DesiError(Exception):
    """Base exception for DESI∞ errors."""


class ValidationError(DesiError, ValueError):
    """Raised when input data fails validation."""


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be a real number, not {type(value).__name__}.")
    try:
        number = float(value)
    except OverflowError as error:
        raise ValueError(f"{label} is outside the supported numeric range.") from error
    if not isfinite(number):
        raise ValueError(f"{label} must be finite.")
    return number


# ============================================================
# SECTION 1: GENOMECORE - VERSION 5.0 COMPATIBILITY
# ============================================================

@dataclass(frozen=True)
class MutationResult:
    original_sequence: str
    mutated_sequence: str
    position: int
    original_base: str
    new_base: str

    @property
    def changed(self) -> bool:
        return self.original_base != self.new_base


@dataclass(frozen=True)
class TranslationResult:
    mrna_sequence: str
    amino_acids: Tuple[str, ...]
    codons: Tuple[str, ...]
    stop_found: bool
    incomplete_bases: str

    @property
    def protein_chain(self) -> str:
        return " - ".join(self.amino_acids)

    @property
    def display_protein(self) -> str:
        if not self.stop_found:
            return self.protein_chain
        return f"{self.protein_chain} - STOP" if self.protein_chain else "STOP"


@dataclass(frozen=True)
class TranslationComparison:
    original_mrna: str
    mutated_mrna: str
    original_protein: str
    mutated_protein: str
    original_stop_found: bool
    mutated_stop_found: bool
    protein_chain_changed: bool
    introduced_premature_stop: bool


def validate_dna(dna_sequence: str) -> str:
    if not isinstance(dna_sequence, str):
        raise TypeError("DNA sequence must be a string.")
    sequence = "".join(dna_sequence.split()).upper()
    invalid = sorted(set(sequence) - DNA_BASES)
    if invalid:
        raise ValueError(
            f"Invalid DNA bases: {', '.join(invalid)}. "
            "Only A, T, C and G are accepted."
        )
    return sequence


def validate_rna(rna_sequence: str) -> str:
    if not isinstance(rna_sequence, str):
        raise TypeError("RNA sequence must be a string.")
    sequence = "".join(rna_sequence.split()).upper()
    invalid = sorted(set(sequence) - RNA_BASES)
    if invalid:
        raise ValueError(
            f"Invalid RNA bases: {', '.join(invalid)}. "
            "Only A, U, C and G are accepted."
        )
    return sequence


def calculate_gc_content(dna_sequence: str) -> float:
    sequence = validate_dna(dna_sequence)
    if not sequence:
        return 0.0
    gc_count = sequence.count("G") + sequence.count("C")
    return round(gc_count / len(sequence) * 100, 2)


def simulate_crispr_mutation(
    dna_sequence: str, position: int, new_base: str
) -> MutationResult:
    """Legacy-compatible string substitution; not a CRISPR design or edit."""
    sequence = validate_dna(dna_sequence)
    if isinstance(position, bool) or not isinstance(position, int):
        raise TypeError("Position must be an integer.")
    if not 0 <= position < len(sequence):
        raise IndexError(
            f"Position {position} is out of bounds for "
            f"a sequence of length {len(sequence)}."
        )
    if not isinstance(new_base, str):
        raise TypeError("Replacement base must be a string.")
    new_base = new_base.strip().upper()
    if len(new_base) != 1 or new_base not in DNA_BASES:
        raise ValueError("Replacement must be exactly one base: A, T, C or G.")
    original_base = sequence[position]
    mutated_sequence = sequence[:position] + new_base + sequence[position + 1:]
    return MutationResult(sequence, mutated_sequence, position, original_base, new_base)


def transcribe_dna_to_mrna(dna_sequence: str) -> str:
    # Preserves Version 5.0 assumption: supplied DNA is the coding strand.
    return validate_dna(dna_sequence).replace("T", "U")


def translate_mrna(
    mrna_sequence: str, start_at_start_codon: bool = False
) -> TranslationResult:
    sequence = validate_rna(mrna_sequence)
    if not isinstance(start_at_start_codon, bool):
        raise TypeError("start_at_start_codon must be True or False.")

    if start_at_start_codon:
        start_position = sequence.find("AUG")
        if start_position == -1:
            return TranslationResult(sequence, (), (), False, "")
        sequence = sequence[start_position:]

    complete_length = len(sequence) - len(sequence) % 3
    incomplete_bases = sequence[complete_length:]
    amino_acids: List[str] = []
    codons: List[str] = []
    stop_found = False

    for index in range(0, complete_length, 3):
        codon = sequence[index:index + 3]
        amino_acid = CODON_TABLE[codon]
        codons.append(codon)
        if amino_acid == "STOP":
            stop_found = True
            break
        amino_acids.append(amino_acid)

    return TranslationResult(
        sequence, tuple(amino_acids), tuple(codons), stop_found, incomplete_bases
    )


def transcribe_and_translate(
    dna_sequence: str, start_at_start_codon: bool = False
) -> Tuple[str, str]:
    mrna = transcribe_dna_to_mrna(dna_sequence)
    result = translate_mrna(mrna, start_at_start_codon=start_at_start_codon)
    return mrna, result.display_protein


def compare_translations(
    original_dna: str, mutated_dna: str
) -> TranslationComparison:
    original_mrna = transcribe_dna_to_mrna(original_dna)
    mutated_mrna = transcribe_dna_to_mrna(mutated_dna)
    original_result = translate_mrna(original_mrna)
    mutated_result = translate_mrna(mutated_mrna)

    # Improved detection: compare stop positions in the aligned reading frame.
    original_stop_index = next(
        (i for i, c in enumerate(original_result.codons) if c in STOP_CODONS), None
    )
    mutated_stop_index = next(
        (i for i, c in enumerate(mutated_result.codons) if c in STOP_CODONS), None
    )
    introduced_premature_stop = (
        mutated_stop_index is not None
        and (original_stop_index is None or mutated_stop_index < original_stop_index)
    )

    return TranslationComparison(
        original_mrna=original_mrna,
        mutated_mrna=mutated_mrna,
        original_protein=original_result.display_protein,
        mutated_protein=mutated_result.display_protein,
        original_stop_found=original_result.stop_found,
        mutated_stop_found=mutated_result.stop_found,
        protein_chain_changed=original_result.amino_acids != mutated_result.amino_acids,
        introduced_premature_stop=introduced_premature_stop,
    )


# ============================================================
# SECTION 2: PROTEOMECORE
# ============================================================

# Average residue masses (Da) for an unmodified polypeptide residue.
AMINO_ACID_MASS_DA: Dict[str, float] = {
    "Alanine": 71.0788, "Arginine": 156.1875, "Asparagine": 114.1038,
    "Aspartic Acid": 115.0886, "Cysteine": 103.1388, "Glutamic Acid": 129.1155,
    "Glutamine": 128.1307, "Glycine": 57.0519, "Histidine": 137.1411,
    "Isoleucine": 113.1594, "Leucine": 113.1594, "Lysine": 128.1741,
    "Methionine": 131.1926, "Phenylalanine": 147.1766, "Proline": 97.1167,
    "Serine": 87.0782, "Threonine": 101.1051, "Tryptophan": 186.2132,
    "Tyrosine": 163.1760, "Valine": 99.1326,
}
WATER_MASS_DA = 18.01528


@dataclass(frozen=True)
class ProteinReport:
    residue_count: int
    molecular_weight_da: float
    amino_acid_counts: Mapping[str, int]
    unknown_residues: Tuple[str, ...]


def analyze_protein_sequence(sequence: Sequence[str]) -> ProteinReport:
    if isinstance(sequence, str):
        residues = [x.strip().title() for x in sequence.split("-") if x.strip()]
    else:
        residues = [str(x).strip().title() for x in sequence]
    unknown = tuple(sorted({x for x in residues if x not in AMINO_ACID_MASS_DA}))
    if unknown:
        raise ValueError(f"Unknown amino-acid residue(s): {', '.join(unknown)}")
    counts = {name: residues.count(name) for name in sorted(set(residues))}
    # Peptide mass = sum(residue masses) + one water molecule.
    mass = sum(AMINO_ACID_MASS_DA[x] for x in residues)
    if residues:
        mass += WATER_MASS_DA
    return ProteinReport(len(residues), round(mass, 4), counts, unknown)


# ============================================================
# SECTION 3: NEURAL-CARDIAC SIGNAL CORE - COMPATIBLE + HARDENED
# ============================================================

@dataclass
class SignalWindow:
    channel: str
    samples: Sequence[float]
    sample_rate_hz: float
    timestamp_unix: float
    units: str


@dataclass
class SignalReport:
    channel: str
    status: str
    sample_count: int
    duration_seconds: float
    mean_value: Optional[float]
    min_value: Optional[float]
    max_value: Optional[float]
    message: str


def validate_window(window: SignalWindow) -> Optional[str]:
    if not isinstance(window, SignalWindow):
        return "Input must be a SignalWindow."
    if not isinstance(window.channel, str) or not window.channel.strip():
        return "Channel must be a non-empty string."
    if not isinstance(window.units, str) or not window.units.strip():
        return "Units must be a non-empty string."
    try:
        rate = _finite_number(window.sample_rate_hz, "Sample rate")
        timestamp = _finite_number(window.timestamp_unix, "Timestamp")
    except (TypeError, ValueError) as error:
        return str(error)
    if rate <= 0:
        return "Invalid sample rate."
    if isinstance(window.samples, (str, bytes)):
        return "Samples must be a numeric sequence, not text."
    try:
        if len(window.samples) == 0:
            return "No samples received."
        for sample in window.samples:
            _finite_number(sample, "Sample")
    except TypeError as error:
        return str(error)
    except ValueError as error:
        return str(error)
    if timestamp > time() + 5:
        return "Timestamp is unexpectedly in the future."
    if timestamp < 0:
        return "Timestamp cannot be negative."
    return None


def summarize_signal(window: SignalWindow) -> SignalReport:
    error = validate_window(window)
    try:
        n = len(window.samples)
    except TypeError:
        n = 0
    try:
        rate = float(window.sample_rate_hz)
        duration = n / rate if isfinite(rate) and rate > 0 else 0.0
    except (TypeError, ValueError, OverflowError):
        duration = 0.0

    if error:
        return SignalReport(
            channel=getattr(window, "channel", "UNKNOWN"),
            status="DATA_INVALID", sample_count=n, duration_seconds=duration,
            mean_value=None, min_value=None, max_value=None, message=error,
        )

    values = [float(x) for x in window.samples]
    return SignalReport(
        channel=window.channel, status="DATA_RECEIVED", sample_count=n,
        duration_seconds=duration, mean_value=mean(values),
        min_value=min(values), max_value=max(values),
        message="Descriptive statistics only; no clinical interpretation has been performed.",
    )


def process_window(window: SignalWindow) -> SignalReport:
    return summarize_signal(window)


@dataclass(frozen=True)
class SignalQualityReport:
    status: str
    sample_count: int
    flatline: bool
    clipped_sample_count: int
    peak_to_peak: Optional[float]
    standard_deviation: Optional[float]
    warnings: Tuple[str, ...]


def assess_signal_quality(
    window: SignalWindow, flatline_tolerance: float = 1e-12,
    clipping_threshold: Optional[float] = None
) -> SignalQualityReport:
    error = validate_window(window)
    if error:
        return SignalQualityReport("DATA_INVALID", 0, False, 0, None, None, (error,))
    tolerance = _finite_number(flatline_tolerance, "Flatline tolerance")
    if tolerance < 0:
        raise ValueError("Flatline tolerance cannot be negative.")
    if clipping_threshold is not None:
        clipping_threshold = _finite_number(clipping_threshold, "Clipping threshold")
        if clipping_threshold <= 0:
            raise ValueError("Clipping threshold must be positive.")
    values = [float(x) for x in window.samples]
    span = max(values) - min(values)
    flatline = span <= tolerance
    clipped = (
        sum(abs(x) >= clipping_threshold for x in values)
        if clipping_threshold is not None else 0
    )
    warnings = []
    if flatline:
        warnings.append("Signal is constant or nearly constant.")
    if clipped:
        warnings.append("Samples meet or exceed the configured clipping threshold.")
    return SignalQualityReport(
        "REVIEW" if warnings else "QUALITY_CHECK_PASSED",
        len(values), flatline, clipped, span,
        pstdev(values) if len(values) > 1 else 0.0, tuple(warnings)
    )


# ============================================================
# SECTION 4: CARDIOCORE / NEUROCORE - NON-DIAGNOSTIC UTILITIES
# ============================================================

@dataclass(frozen=True)
class IntervalReport:
    interval_count: int
    mean_interval_ms: Optional[float]
    intervals_ms: Tuple[float, ...]
    message: str


def summarize_peak_intervals(
    peak_indices: Sequence[int], sample_rate_hz: float
) -> IntervalReport:
    """Summarize intervals between caller-supplied peak indices; not diagnosis."""
    rate = _finite_number(sample_rate_hz, "Sample rate")
    if rate <= 0:
        raise ValueError("Sample rate must be positive.")
    if len(peak_indices) < 2:
        return IntervalReport(0, None, (), "At least two peak indices are required.")
    indices = []
    for index in peak_indices:
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError("Peak indices must be integers.")
        indices.append(index)
    if any(x < 0 for x in indices):
        raise ValueError("Peak indices cannot be negative.")
    if any(b <= a for a, b in zip(indices, indices[1:])):
        raise ValueError("Peak indices must be strictly increasing.")
    intervals = tuple(round((b - a) / rate * 1000, 3)
                      for a, b in zip(indices, indices[1:]))
    return IntervalReport(
        len(intervals), round(mean(intervals), 3), intervals,
        "Mathematical interval summary only; peak validity and clinical meaning are not assessed."
    )


# ============================================================
# SECTION 5: DESI INTELLIGENCE ENGINE - SIMPLE EXPLAINABLE FLAGGING
# ============================================================

@dataclass(frozen=True)
class AnomalyReport:
    flagged_indices: Tuple[int, ...]
    center: Optional[float]
    median_absolute_deviation: Optional[float]
    method: str
    message: str


def detect_statistical_outliers(
    values: Sequence[float], threshold: float = 3.5
) -> AnomalyReport:
    """Robust univariate outlier flagging; not an AI diagnosis."""
    if not values:
        return AnomalyReport((), None, None, "modified_z_score", "No data supplied.")
    data = [_finite_number(x, "Data value") for x in values]
    cutoff = _finite_number(threshold, "Threshold")
    if cutoff <= 0:
        raise ValueError("Threshold must be positive.")
    center = median(data)
    mad = median([abs(x - center) for x in data])
    if mad == 0:
        # With zero MAD, only values different from the median are flagged.
        flagged = tuple(i for i, x in enumerate(data) if x != center)
    else:
        flagged = tuple(
            i for i, x in enumerate(data)
            if 0.67448975 * abs(x - center) / mad > cutoff
        )
    return AnomalyReport(
        flagged, center, mad, "modified_z_score",
        "Statistical flags require human review; they do not establish a cause or diagnosis."
    )


# ============================================================
# SECTION 6: BIOPHYSICSCORE - GENERAL MATHEMATICAL MODEL
# ============================================================

@dataclass(frozen=True)
class OscillatorResult:
    displacement: float
    velocity: float
    angular_frequency_rad_s: float
    message: str


def simple_harmonic_oscillator(
    amplitude: float, frequency_hz: float, time_seconds: float,
    phase_radians: float = 0.0
) -> OscillatorResult:
    """Idealized x=A*cos(2*pi*f*t+phase) model; not a biological prediction."""
    a = _finite_number(amplitude, "Amplitude")
    f = _finite_number(frequency_hz, "Frequency")
    t = _finite_number(time_seconds, "Time")
    phase = _finite_number(phase_radians, "Phase")
    if f < 0 or t < 0:
        raise ValueError("Frequency and time must be non-negative.")
    omega = 2.0 * 3.141592653589793 * f
    angle = omega * t + phase
    return OscillatorResult(
        a * cos(angle),
        -a * omega * sin(angle),
        omega,
        "Ideal mathematical model; not a patient-specific biological simulation."
    )


# ============================================================
# SECTION 7: NANOMEDCORE - UNIT CONVERSION / RESEARCH CALCULATOR
# ============================================================

@dataclass(frozen=True)
class ConcentrationResult:
    value_mol_per_litre: float
    source_unit: str
    message: str


def convert_concentration_to_molar(value: float, unit: str) -> ConcentrationResult:
    """Convert molar concentration units only; no dose or treatment guidance."""
    amount = _finite_number(value, "Concentration")
    if amount < 0:
        raise ValueError("Concentration cannot be negative.")
    factors = {
        "M": 1.0, "mM": 1e-3, "uM": 1e-6, "µM": 1e-6,
        "nM": 1e-9, "pM": 1e-12,
    }
    if unit not in factors:
        raise ValueError(f"Unsupported concentration unit: {unit}")
    return ConcentrationResult(
        amount * factors[unit], unit,
        "Unit conversion only; not a dosage, safety, or treatment recommendation."
    )


# ============================================================
# SECTION 8: IMAGINGCORE - BASIC NUMERICAL IMAGE UTILITIES
# ============================================================

def validate_grayscale_image(image: Sequence[Sequence[float]]) -> List[List[float]]:
    if isinstance(image, (str, bytes)) or not image:
        raise ValueError("Image must be a non-empty 2D numeric matrix.")
    rows = []
    width = None
    for row in image:
        if isinstance(row, (str, bytes)) or not row:
            raise ValueError("Image rows must be non-empty numeric sequences.")
        converted = [_finite_number(pixel, "Pixel") for pixel in row]
        if width is None:
            width = len(converted)
        elif len(converted) != width:
            raise ValueError("Image matrix must be rectangular.")
        if any(pixel < 0 or pixel > 255 for pixel in converted):
            raise ValueError("Grayscale pixel values must be between 0 and 255.")
        rows.append(converted)
    return rows


def grayscale_image_summary(image: Sequence[Sequence[float]]) -> Dict[str, float]:
    matrix = validate_grayscale_image(image)
    pixels = [pixel for row in matrix for pixel in row]
    return {
        "width_pixels": float(len(matrix[0])),
        "height_pixels": float(len(matrix)),
        "pixel_count": float(len(pixels)),
        "mean_intensity": round(mean(pixels), 4),
        "minimum_intensity": min(pixels),
        "maximum_intensity": max(pixels),
    }


# ============================================================
# SECTION 9: RESEARCHCORE / SECURITYCORE
# ============================================================

def canonical_json(data: Any) -> str:
    def convert(value: Any) -> Any:
        if is_dataclass(value):
            return convert(asdict(value))
        if isinstance(value, Mapping):
            converted = {}
            for key, item in value.items():
                string_key = str(key)
                if string_key in converted:
                    raise ValueError(
                        f"Mapping keys collide after JSON string conversion: {string_key!r}"
                    )
                converted[string_key] = convert(item)
            return converted
        if isinstance(value, (list, tuple)):
            return [convert(v) for v in value]
        if isinstance(value, (str, int, float, bool)) or value is None:
            if isinstance(value, float) and not isfinite(value):
                raise ValueError("Non-finite values cannot be serialized.")
            return value
        raise TypeError(f"Unsupported data type for JSON export: {type(value).__name__}")
    return json.dumps(convert(data), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def calculate_sha256(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    if not isinstance(data, bytes):
        raise TypeError("SHA-256 input must be str or bytes.")
    return sha256(data).hexdigest()


def export_research_json(data: Any, output_path: str | Path) -> str:
    """Write structured research data as JSON; returns the resulting path."""
    path = Path(output_path)
    if path.suffix.lower() != ".json":
        raise ValueError("Research export path must end in .json.")
    serialized = canonical_json(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json.loads(serialized), indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return str(path)


# ============================================================
# SECTION 10: MASTER SYSTEM SELF-CHECK
# ============================================================

@dataclass(frozen=True)
class SystemCheck:
    module_name: str
    version: str
    codon_count: int
    codon_table_complete: bool
    compatibility_version: str
    status: str
    message: str


def run_system_check() -> SystemCheck:
    all_codons = {
        a + b + c for a in "AUCG" for b in "AUCG" for c in "AUCG"
    }
    missing = all_codons - set(CODON_TABLE)
    extra = set(CODON_TABLE) - all_codons
    complete = not missing and not extra and len(CODON_TABLE) == 64
    return SystemCheck(
        MODULE_NAME, MODULE_VERSION, len(CODON_TABLE), complete,
        COMPATIBILITY_VERSION, "READY" if complete else "CHECK_REQUIRED",
        "All 64 standard codons verified." if complete
        else f"Codon table mismatch. Missing={sorted(missing)}, extra={sorted(extra)}"
    )


# ============================================================
# SECTION 11: AUTOMATED VALIDATION TESTS
# ============================================================

class TestDesiInfinity60(unittest.TestCase):
    # Version 5.0 compatibility tests
    def test_gc_content(self):
        self.assertEqual(calculate_gc_content("ATGC"), 50.0)

    def test_empty_gc_content(self):
        self.assertEqual(calculate_gc_content(""), 0.0)

    def test_invalid_dna(self):
        with self.assertRaises(ValueError):
            validate_dna("ATGX")

    def test_mutation_position(self):
        self.assertEqual(simulate_crispr_mutation("ATGC", 1, "C").mutated_sequence, "ACGC")

    def test_mutation_bounds(self):
        with self.assertRaises(IndexError):
            simulate_crispr_mutation("ATGC", 4, "A")

    def test_transcription(self):
        self.assertEqual(transcribe_dna_to_mrna("ATGGCT"), "AUGGCU")

    def test_translation(self):
        result = translate_mrna("AUGGCUUAA")
        self.assertEqual(result.amino_acids, ("Methionine", "Alanine"))
        self.assertTrue(result.stop_found)

    def test_all_64_codons(self):
        self.assertEqual(len(CODON_TABLE), 64)
        self.assertEqual(run_system_check().status, "READY")

    def test_nonsense_comparison(self):
        result = compare_translations("ATGGCCTGG", "ATGGCCTAA")
        self.assertTrue(result.introduced_premature_stop)

    # New reliability tests
    def test_bool_rejected_as_sample(self):
        window = SignalWindow("ECG", [True, 0.2], 100.0, time(), "mV")
        self.assertEqual(process_window(window).status, "DATA_INVALID")

    def test_nan_sample_rate_rejected(self):
        window = SignalWindow("ECG", [0.1], float("nan"), time(), "mV")
        self.assertEqual(process_window(window).status, "DATA_INVALID")

    def test_huge_integer_sample_rate_rejected_without_crash(self):
        window = SignalWindow("ECG", [0.1], 10 ** 10000, time(), "mV")
        self.assertEqual(process_window(window).status, "DATA_INVALID")

    def test_json_mapping_key_collision_rejected(self):
        with self.assertRaises(ValueError):
            canonical_json({1: "integer key", "1": "string key"})

    def test_infinite_timestamp_rejected(self):
        window = SignalWindow("ECG", [0.1], 100.0, float("inf"), "mV")
        self.assertEqual(process_window(window).status, "DATA_INVALID")

    def test_empty_signal(self):
        window = SignalWindow("ECG", [], 100.0, time(), "mV")
        self.assertEqual(process_window(window).status, "DATA_INVALID")

    def test_signal_quality_flatline(self):
        window = SignalWindow("ECG", [1.0, 1.0, 1.0], 100.0, time(), "mV")
        self.assertTrue(assess_signal_quality(window).flatline)

    def test_peak_intervals(self):
        result = summarize_peak_intervals([0, 100, 200], 100.0)
        self.assertEqual(result.intervals_ms, (1000.0, 1000.0))

    def test_peak_order_rejected(self):
        with self.assertRaises(ValueError):
            summarize_peak_intervals([0, 100, 90], 100.0)

    def test_outlier_detection(self):
        result = detect_statistical_outliers([1, 1, 1, 1, 20])
        self.assertIn(4, result.flagged_indices)

    def test_protein_analysis(self):
        result = analyze_protein_sequence(["Methionine", "Alanine"])
        self.assertEqual(result.residue_count, 2)
        self.assertGreater(result.molecular_weight_da, 0)

    def test_invalid_protein_residue(self):
        with self.assertRaises(ValueError):
            analyze_protein_sequence(["UnknownResidue"])

    def test_concentration_conversion(self):
        result = convert_concentration_to_molar(2, "mM")
        self.assertAlmostEqual(result.value_mol_per_litre, 0.002)

    def test_invalid_concentration_unit(self):
        with self.assertRaises(ValueError):
            convert_concentration_to_molar(1, "unknown")

    def test_image_summary(self):
        result = grayscale_image_summary([[0, 100], [200, 255]])
        self.assertEqual(result["pixel_count"], 4.0)
        self.assertEqual(result["mean_intensity"], 138.75)

    def test_ragged_image_rejected(self):
        with self.assertRaises(ValueError):
            validate_grayscale_image([[0, 1], [2]])

    def test_sha256(self):
        self.assertEqual(
            calculate_sha256("abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        )

    def test_json_serialization(self):
        serialized = canonical_json({"b": 2, "a": 1})
        self.assertEqual(serialized, '{"a":1,"b":2}')

    def test_oscillator(self):
        result = simple_harmonic_oscillator(2, 1, 0)
        self.assertAlmostEqual(result.displacement, 2.0)

    def test_legacy_comparison_stop_position(self):
        # Original has a stop at codon 3; mutated introduces one at codon 2.
        result = compare_translations("ATGGCTTAATGG", "ATGTAGTAATGG")
        self.assertTrue(result.introduced_premature_stop)


# ============================================================
# SECTION 12: MAIN EXECUTION
# ============================================================

def main() -> None:
    basicConfig(level=INFO, format="%(levelname)s: %(message)s")
    print("=" * 68)
    print(MODULE_NAME)
    print(f"Version: {MODULE_VERSION} | V5 compatibility: {COMPATIBILITY_VERSION}")
    print("=" * 68)

    check = run_system_check()
    print("\n>>> MASTER SYSTEM SELF-CHECK")
    print(f"Status: {check.status}")
    print(f"Codons: {check.codon_count}/64")
    print(check.message)

    print("\n>>> GENOMECORE DEMONSTRATION")
    demo_dna = "ATGGACGAGACCATGAAGGAGTTGAAGGCCTACAAATCGGAAGAGCTGG"
    print(f"DNA length: {len(validate_dna(demo_dna))}")
    print(f"GC content: {calculate_gc_content(demo_dna)}%")
    mutation = simulate_crispr_mutation(demo_dna, 15, "T")
    comparison = compare_translations(demo_dna, mutation.mutated_sequence)
    print(f"Mutation changed sequence: {mutation.changed}")
    print(f"Protein chain changed: {comparison.protein_chain_changed}")
    print(f"Earlier/new stop detected: {comparison.introduced_premature_stop}")

    print("\n>>> NEURAL-CARDIAC SIGNAL QUALITY DEMONSTRATION")
    demo_signal = SignalWindow(
        "DEMO_ECG_CHANNEL", [0.1, 0.2, 0.15, 0.12, 0.18],
        100.0, time(), "mV"
    )
    print(summarize_signal(demo_signal))
    print(assess_signal_quality(demo_signal))

    print("\n>>> ADDITIONAL CORE CHECKS")
    print(analyze_protein_sequence(["Methionine", "Alanine"]))
    print(convert_concentration_to_molar(2, "mM"))
    print(grayscale_image_summary([[0, 100], [200, 255]]))
    print(f"SHA-256 demo: {calculate_sha256('DESI_INFINITY_SYSTEM_6.0')}")
    print("\nDESI∞ MASTER CORE DEMONSTRATION COMPLETE.")
    print("Research/educational computation only; not for clinical use.")


if __name__ == "__main__":
    main()
    print("\nRunning DESI∞ 6.0 automated validation tests...")
    unittest.main(argv=["desi_master_core"], exit=False, verbosity=2)