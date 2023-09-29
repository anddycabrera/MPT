FROM nvcr.io/nvidia/pytorch:22.12-py3
RUN pip uninstall torch -y

WORKDIR /workspace

COPY /inference/vllm /workspace/inference/vllm
WORKDIR /workspace/inference/vllm
RUN pip install -e .

ENV PYTHONPATH=/workspace/inference/vllm

EXPOSE 8000
CMD ["python", "-m", "vllm.entrypoints.openai.api_server", "--host", "0.0.0.0"]