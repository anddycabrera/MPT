FROM nvcr.io/nvidia/tritonserver:23.08-py3

WORKDIR /work

COPY . /work/
RUN chmod +x gen_vllm_env.sh && ./gen_vllm_env.sh