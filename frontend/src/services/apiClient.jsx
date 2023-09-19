import { Url } from "./utils";
export function apiClient(url, method = "get", body = {}, public_api = false, isStreaming = false, onChunkReceived) {
    const baseUrl = Url();
    const config = {
        method: method,
        headers: {
            "Content-Type": "application/json",
        },
    };
    
    if (method.toLowerCase() !== "get" && method.toLowerCase() !== "delete") {
        config.body = body;
    }
    
    if (isStreaming) {
        return new Promise((resolve, reject) => {
            fetch(baseUrl + url, config)
                .then(response => {
                    if (!response.ok) {
                        reject('Network response was not ok');
                        return;
                    }
                    
                    let data = '';
                    const reader = response.body.getReader();
                    reader.read().then(function processText({ done, value }) {
                        const chunk = new TextDecoder().decode(value);
                        data += chunk;
                        if (onChunkReceived) {
                            onChunkReceived(chunk); // Call the provided callback with the chunk.
                        }
                        if (done) {
                            resolve(data);
                            return;
                        }
                        reader.read().then(processText);
                    });
                })
                .catch(error => {
                    reject(error);
                });
        });
    } else {
        return fetch(baseUrl + url, config)
            .then((response) => {
                if (response.ok) {
                    return response.json();
                } else if (response.status === 204 && method.toLowerCase() === "delete") {
                    return response.json();
                }
            })
            .catch((error) => {
                console.log(error);
            });
    }
}