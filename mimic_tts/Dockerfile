FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

WORKDIR /app

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HF_HOME=/root/.cache/huggingface

#
# System dependencies
#
RUN apt-get update && apt-get install -y \
    sox \
    libsox-fmt-all \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*


#
# Python dependencies
#
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


#
# Runtime folders
#
RUN mkdir -p \
    /app/app \
    /app/models \
    /app/voices \
    /app/input \
    /app/output \
    /app/config


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]