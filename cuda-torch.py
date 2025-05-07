import torch
print(f"CUDA tersedia: {torch.cuda.is_available()}")
print(f"Versi CUDA: {torch.version.cuda}")