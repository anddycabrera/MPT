import json
import queue

import numpy as np
import tritonclient.grpc.aio as grpcclient
from tritonclient.utils import *


class UserData:
    def __init__(self):
        self._completed_requests = queue.Queue()


def create_request(prompt, stream, request_id, sampling_parameters, model_name):
    inputs = []
    prompt_data = np.array([prompt.encode("utf-8")], dtype=np.object_)
    try:
        inputs.append(grpcclient.InferInput("PROMPT", [1], "BYTES"))
        inputs[-1].set_data_from_numpy(prompt_data)
    except Exception as e:
        print(f"Encountered an error {e}")

    stream_data = np.array([stream], dtype=bool)
    inputs.append(grpcclient.InferInput("STREAM", [1], "BOOL"))
    inputs[-1].set_data_from_numpy(stream_data)

    # Add requested outputs
    outputs = []
    outputs.append(grpcclient.InferRequestedOutput("TEXT"))

    # Issue the asynchronous sequence inference.
    return {
        "model_name": model_name,
        "inputs": inputs,
        "outputs": outputs,
        "request_id": str(request_id),
        "parameters": sampling_parameters,
    }


async def model_client(FLAGS, prompt_text, model_name = "vllm", sampling_parameters = {"temperature": "0.1", "top_p": "0.15"}):
    stream = FLAGS.streaming_mode
    prompts = [prompt_text]

    results_dict = {}

    async with grpcclient.InferenceServerClient(
        url=FLAGS.url, verbose=FLAGS.verbose
    ) as triton_client:
        # Request iterator that yields the next request
        async def async_request_iterator():
            try:
                for iter in range(FLAGS.iterations):
                    for i, prompt in enumerate(prompts):
                        prompt_id = FLAGS.offset + (len(prompts) * iter) + i
                        results_dict[str(prompt_id)] = []
                        yield create_request(
                            prompt, stream, prompt_id, sampling_parameters, model_name
                        )
            except Exception as error:
                print(f"caught error in request iterator:  {error}")

        try:
            # Start streaming
            response_iterator = triton_client.stream_infer(
                inputs_iterator=async_request_iterator(),
                stream_timeout=FLAGS.stream_timeout,
            )
            # Read response from the stream
            async for response in response_iterator:
                result, error = response
                if error:
                    print(f"Encountered error while processing: {error}")
                else:
                    output = result#.as_numpy("TEXT")
                    for i in output:
                        data = json.loads(i.decode("utf-8"))
                        out = data["text"]
                        yield out

        except InferenceServerException as error:
            print(error)
