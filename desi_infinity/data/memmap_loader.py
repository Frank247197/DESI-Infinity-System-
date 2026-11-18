# ============================================================
# DESI∞ INFINITY SYSTEM 6.1 - ZERO-COPY DATA LOADER MODULE
# High-Throughput Memory-Mapped Tensor Pipeline for Genomics & MD
# ============================================================

import os
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from typing import Tuple, Optional


class ZeroCopyBioDataset(Dataset):
    """
    [SIM] Memory-mapped PyTorch Dataset for multi-gigabyte genomic arrays 
    and nanoparticle trajectory data. Streams data slices directly 
    from disk without loading the full dataset into RAM.
    """

    def __init__(
        self, 
        filepath: str, 
        shape: Tuple[int, ...], 
        dtype: np.dtype = np.float32,
        target_filepath: Optional[str] = None,
        target_shape: Optional[Tuple[int, ...]] = None
    ):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Memory-mapped feature file not found: {filepath}")
        if any(dim <= 0 for dim in shape):
            raise ValueError(f"Invalid tensor shape {shape}. All dimensions must be positive.")

        self.filepath = filepath
        self.shape = shape
        self.dtype = dtype

        # Open read-only memory map (OS manages paging automatically)
        self.data = np.memmap(self.filepath, dtype=self.dtype, mode="r", shape=self.shape)

        self.targets = None
        if target_filepath is not None:
            if not os.path.exists(target_filepath):
                raise FileNotFoundError(f"Target file not found: {target_filepath}")
            if target_shape is None or any(dim <= 0 for dim in target_shape):
                raise ValueError("Valid target_shape must be provided with target_filepath.")
            self.targets = np.memmap(target_filepath, dtype=self.dtype, mode="r", shape=target_shape)

    def __len__(self) -> int:
        return self.shape[0]

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, ...]:
        # Zero-copy conversion from numpy slice to PyTorch tensor
        x_slice = np.array(self.data[idx], copy=False)
        x_tensor = torch.from_numpy(x_slice)

        if self.targets is not None:
            y_slice = np.array(self.targets[idx], copy=False)
            y_tensor = torch.from_numpy(y_slice)
            return x_tensor, y_tensor

        return (x_tensor,)


def create_synthetic_memmap(filepath: str, shape: Tuple[int, ...], seed: int = 42) -> None:
    """
    Utility to generate seed-locked binary memmap files on disk 
    without holding the entire array in RAM at once.
    """
    rng = np.random.default_rng(seed)
    fp = np.memmap(filepath, dtype=np.float32, mode="w+", shape=shape)
    
    # Write in chunks to keep RAM footprint near zero
    chunk_size = 1000
    for start in range(0, shape[0], chunk_size):
        end = min(start + chunk_size, shape[0])
        fp[start:end] = rng.standard_normal((end - start, *shape[1:])).astype(np.float32)
    
    fp.flush()
    del fp  # Close file handle cleanly


if __name__ == "__main__":
    print("=" * 60)
    print("DESI∞ ZERO-COPY MEMMAP DATASET VERIFICATION [SIM]")
    print("=" * 60)

    sample_file = "temp_genomic_features.dat"
    dataset_shape = (50000, 128)  # 50,000 sequences, 128 features each

    try:
        print(f"\n[1] Generating seed-locked memmap binary ({dataset_shape})...")
        create_synthetic_memmap(sample_file, dataset_shape, seed=42)

        print("[2] Initializing ZeroCopyBioDataset & PyTorch DataLoader...")
        dataset = ZeroCopyBioDataset(filepath=sample_file, shape=dataset_shape)
        loader = DataLoader(dataset, batch_size=64, shuffle=True, num_workers=0)

        first_batch = next(iter(loader))[0]
        print(f"  Batch Tensor Shape : {first_batch.shape}")
        print(f"  Batch Dtype        : {first_batch.dtype}")
        print(f"  Memory Footprint   : Streamed directly from disk (Zero-Copy)")

    finally:
        # Clean up temporary test binary
        if os.path.exists(sample_file):
            os.remove(sample_file)
            print("\n[3] Temporary verification binary cleaned up.")
