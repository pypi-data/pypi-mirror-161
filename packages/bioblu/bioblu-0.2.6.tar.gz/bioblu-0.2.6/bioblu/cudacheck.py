#!/usr/bin/env python3
import torch
import tensorflow as tf

print("CUDA check:")
if torch.cuda.device_count() > 0:
    print(f"Current device:".ljust(20) + f"{torch.cuda.current_device()}")
    print(f"CUDA device count:".ljust(20) + f"{torch.cuda.device_count()}")
    print(f"CUDA device name:".ljust(20) + f"{torch.cuda.get_device_name(0)}")
    print(f"CUDA available:".ljust(20) + f"{torch.cuda.is_available()}")
else:
    print("No CUDA device.")

# print(f"Tensorflow: GPU is available: {tf.test.is_gpu_available()}")  # Deprecated
print(f"Tensorflow: Physical GPU devices: {tf.config.list_physical_devices('GPU')}")
