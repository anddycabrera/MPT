import asyncio
import gradio as gr
from client import model_client 

def sync_model_streaming_chat(prompt_text, model_name="vllm", sampling_parameters={"temperature": "0.1", "top_p": "0.95"}):
    # You'll need to define FLAGS or pass the necessary parameters directly.
    # For this example, I'm assuming you define FLAGS here, but you might want to customize it.
    class FLAGS:
        verbose = False
        url = "tritonserver:8001"
        stream_timeout = None
        offset = 0
        iterations = 1
        streaming_mode = True

    # Run the asynchronous function.
    results = asyncio.run(model_client(FLAGS, prompt_text, model_name, sampling_parameters))
    return results

# Define the interface with the server_port parameter set.
iface = gr.ChatInterface(fn=sync_model_streaming_chat)
iface.launch()

