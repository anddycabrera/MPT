import argparse
import json
import requests
import gradio as gr


def http_bot(message, history):
    headers = {"User-Agent": "vLLM Client"}
    pload = {
        "n": 1,
        "temperature": 0.1,
        "prompt": message,  # use message from the chat interface here
        "stream": True,
        "max_tokens": 2048,
        "frequency_penalty": 1.2,
        "top_p": 0.15

    }
    response = requests.post(args.model_url,
                             headers=headers,
                             json=pload,
                             stream=True)

    for chunk in response.iter_lines(chunk_size=8192,
                                     decode_unicode=False,
                                     delimiter=b"\0"):
        if chunk:
            data = json.loads(chunk.decode("utf-8"))
            output = data["text"][0]
            yield output  # sending output as a message in chat interface


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--model-url",
                        type=str,
                        default="http://localhost:8000/generate")
    args = parser.parse_args()

    custom_textbox = gr.inputs.Textbox(lines=10, placeholder="Type here...")

    chat_interface = gr.ChatInterface(fn=http_bot, textbox=custom_textbox)
    chat_interface.queue(concurrency_count=100).launch(server_name=args.host, server_port=args.port, share=True)
