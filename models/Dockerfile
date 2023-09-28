# Use the specified image
FROM nvcr.io/nvidia/pytorch:22.12-py3

# Install the vllm package
RUN pip install vllm==0.1.7

# Set the working directory
WORKDIR /work

# Copy the requirements file and install the requirements
COPY ./requirements.txt /work
RUN pip install --no-cache-dir -r requirements.txt

# Set the entrypoint to start the application
ENTRYPOINT ["python", "-m", "vllm.entrypoints.api_server"]
