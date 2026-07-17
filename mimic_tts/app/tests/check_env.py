import torch
import torchvision
import torchaudio
import transformers
import qwen_tts


print("=" * 50)
print("Environment Check")
print("=" * 50)

print("Torch:")
print(torch.__version__)

print("CUDA:")
print(torch.version.cuda)

print("GPU Available:")
print(torch.cuda.is_available())

if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))

print("Torchvision:")
print(torchvision.__version__)

print("Torchaudio:")
print(torchaudio.__version__)

print("Transformers:")
print(transformers.__version__)

print("Qwen:")
print(qwen_tts.__file__)

print("=" * 50)