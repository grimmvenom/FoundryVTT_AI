# ComfyUI [No Longer Used in this project]


- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

## ComfyUI Plugins

- [ComfyUI Manager](https://github.com/Comfy-Org/ComfyUI-Manager)
- ~~[ComfyUI-Qwen3-TTS by wanaigc](https://github.com/wanaigc/ComfyUI-Qwen3-TTS)~~
- [ComfyUI-Qwen-TTS by Flybirdxx](https://github.com/flybirdxx/ComfyUI-Qwen-TTS)
- [ComfyUI-Whisper](https://github.com/yuvraj108c/ComfyUI-Whisper)
- [FLUX Kontext]() - Image Generation
- [https://www.youtube.com/watch?v=bZy-BvO7Xk8](https://www.youtube.com/watch?v=bZy-BvO7Xk8)


## FLUX Kontext Models:
```
ai_data/
└── comfyui/
    └── models/
        ├── diffusion_models/
        │   └── flux1-dev-kontext_fp8_scaled.safetensors
        │
        ├── text_encoders/
        │   ├── clip_l.safetensors
        │   └── t5xxl_fp8_e4m3fn_scaled.safetensors
        │
        └── vae/
            └── ae.safetensors
```
Those are the model locations/files specified by ComfyUI's native Kontext documentation.

The big one is:
- flux1-dev-kontext_fp8_scaled.safetensors — ~11.9 GB
- The Comfy-Org version is specifically packaged for ComfyUI.
- The FP8 T5 encoder is another ~5.16 GB.

So budget roughly 18 GB of disk space for the complete setup.



## Build ComfyUI container:
```
cd comfyui
docker compose build comfyui
docker compose up -d comfyui
```


## Install FLUX Kontext models:
```
docker compose exec comfyui /usr/local/bin/download_flux_kontext_models.sh
```