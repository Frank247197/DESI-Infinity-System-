# ============================================================
# DESI∞ INFINITY SYSTEM 6.1 - GENOMCORE MODULE
# Computational Genomics & Molecular Biology
# ============================================================

class GenomCore:
    def __init__(self):
        self.name = "GENOMCORE"
        self.version = "6.1"
        self.dna_bases = set("ATCG")
        self.rna_bases = set("AUCG")
        self.codon_table = {
            "UUU": "Phenylalanine", "UUC": "Phenylalanine", "UUA": "Leucine", "UUG": "Leucine",
            "CUU": "Leucine", "CUC": "Leucine", "CUA": "Leucine", "CUG": "Leucine",
            "AUU": "Isoleucine", "AUC": "Isoleucine", "AUA": "Isoleucine", "AUG": "Methionine",
            "GUU": "Valine", "GUC": "Valine", "GUA": "Valine", "GUG": "Valine",
            "UCU": "Serine", "UCC": "Serine", "UCA": "Serine", "UCG": "Serine",
            "AGU": "Serine", "AGC": "Serine", "CCU": "Proline", "CCC": "Proline",
            "CCA": "Proline", "CCG": "Proline", "ACU": "Threonine", "ACC": "Threonine",
            "ACA": "Threonine", "ACG": "Threonine", "GCU": "Alanine", "GCC": "Alanine",
            "GCA": "Alanine", "GCG": "Alanine", "UAU": "Tyrosine", "UAC": "Tyrosine",
            "UAA": "STOP", "UAG": "STOP", "UGA": "STOP", "CAU": "Histidine",
            "CAC": "Histidine", "CAA": "Glutamine", "CAG": "Glutamine", "AAU": "Asparagine",
            "AAC": "Asparagine", "AAA": "Lysine", "AAG": "Lysine", "GAU": "Aspartic Acid",
            "GAC": "Aspartic Acid", "GAA": "Glutamic Acid", "GAG": "Glutamic Acid",
            "UGU": "Cysteine", "UGC": "Cysteine", "UGG": "Tryptophan", "CGU": "Arginine",
            "CGC": "Arginine", "CGA": "Arginine", "CGG": "Arginine", "AGA": "Arginine",
            "AGG": "Arginine", "GGU": "Glycine", "GGC": "Glycine", "GGA": "Glycine",
            "GGG": "Glycine"
        }

    def validate_dna(self, sequence):
        seq = "".join(sequence.split()).upper()
        if not set(seq).issubset(self.dna_bases):
            raise ValueError("Invalid DNA sequence. Only A, T, C, G allowed.")
        return seq

    def calculate_gc_content(self, sequence):
        seq = self.validate_dna(sequence)
        if not seq: return 0.0
        gc = seq.count("G") + seq.count("C")
        return round((gc / len(seq)) * 100, 2)

    def transcribe_dna_to_mrna(self, sequence):
        seq = self.validate_dna(sequence)
        return seq.replace("T", "U")

    def translate_mrna(self, sequence):
        seq = "".join(sequence.split()).upper()
        if not set(seq).issubset(self.rna_bases):
            raise ValueError("Invalid RNA sequence.")
        
        protein = []
        for i in range(0, len(seq) - 2, 3):
            codon = seq[i:i+3]
            amino_acid = self.codon_table.get(codon, "Unknown")
            if amino_acid == "STOP":
                break
            protein.append(amino_acid)
        return " - ".join(protein)

    def compare_sequences(self, seq1, seq2):
        s1 = self.validate_dna(seq1)
        s2 = self.validate_dna(seq2)
        if len(s1) != len(s2):
            raise ValueError("Sequences must be the same length for comparison.")
        
        mutations = 0
        for a, b in zip(s1, s2):
            if a != b:
                mutations += 1
        return {
            "length": len(s1),
            "mutations": mutations,
            "similarity_%": round(((len(s1) - mutations) / len(s1)) * 100, 2)
        }

# ============================================================
# DEMONSTRATION
# ============================================================
if __name__ == "__main__":
    core = GenomCore()
    print("="*50)
    print(f"DESI∞ {core.name} v{core.version} Initialized")
    print("="*50)
    
    # Example Patient DNA
    dna = "ATGGACGAGACCATGAAGGAGTTGAAGGCCTACAAATCGGAAGAGCTGG"
    
    print(f"\nDNA Sequence: {dna}")
    print(f"GC Content: {core.calculate_gc_content(dna)}%")
    
    # Transcribe and Translate
    mrna = core.transcribe_dna_to_mrna(dna)
    protein = core.translate_mrna(mrna)
    print(f"\nmRNA: {mrna}")
    print(f"Protein: {protein}")
    
    # Mutation comparison
    mutated_dna = "ATGGACGAGACCATGTAGGAGTTGAAGGCCTACAAATCGGAAGAGCTGG"
    comparison = core.compare_sequences(dna, mutated_dna)
    print(f"\nMutation Analysis:")
    print(f"  Original length: {comparison['length']}")
    print(f"  Mutations found: {comparison['mutations']}")
    print(f"  Similarity: {comparison['similarity_%']}%")
