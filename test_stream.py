# import json

# import requests

# url = "http://localhost:8000/api/v1/openai/stream_chat"
# message = "what is langchain stream?"
# data = {"question": message, "session_id": "string"}

# headers = {"Content-type": "application/json"}

# with requests.post(url, data=json.dumps(data), headers=headers, stream=True) as r:
#     for chunk in r.iter_content(1024):
#         print(chunk)


import requests
import base64

# Encode your text input
text_input = "what is your name?"
encoded_input = base64.b64encode(text_input.encode('utf-8')).decode('utf-8')

# Define endpoint and headers
url = "http://129.80.165.66:8001/v2/models/vllm/versions/1/infer"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your_optional_token_if_required"
}

# Define your data payload
# This structure can vary based on the model's expected input format
data = {
    "id": "some_unique_request_id",
    "inputs": [
        {
            "name": "input_tensor_name",
            "datatype": "BYTES",
            "shape": [1],
            "data": [encoded_input]
        }
    ]
}

# Send POST request
response = requests.post(url, headers=headers, json=data)
print(response.json())

