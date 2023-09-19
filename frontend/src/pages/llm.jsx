import React, { useEffect, useState } from "react";
import { Card } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { v4 as uuidv4 } from 'uuid';
import { apiClient } from "../services/apiClient";

function LLM() {
    const generateSessionId = () => {
        return uuidv4();
    };
    const { question } = useParams();
    const defaultBotMessage = "Hi, wellcome to Vector Solutions Bot, how can I help you today?";
    const [input, setInput] = useState('');
    const [chatHistory, setChatHistory] = useState([{message: defaultBotMessage, type: 'api'}]);
    const [sessionId, setSessionId] = useState(null);
    const [currentAPIMessage, setCurrentAPIMessage] = useState('');

    useEffect(() => {
        if (!sessionId) {
            setSessionId(generateSessionId());
        }
    }, []);
    useEffect(() => {
        if (question && sessionId) {
            const decodedQuestion = decodeURIComponent(question);
            sendToAPI(decodedQuestion);
            setInput('');
        }
    }, [question, sessionId]);
    const sendToAPI = (userInput) => {
        try {
            setChatHistory(prevChatHistory => [...prevChatHistory, { message: userInput, type: 'user' }]);
            
            apiClient('openai/chat-ai', 'POST',
            JSON.stringify({
                question: userInput,
                session_id: sessionId
            }), false, true, (chunk) => {
                setCurrentAPIMessage(prevMessage => prevMessage + chunk);
                            })
            .then(completeMessage => {
                setChatHistory(prevChatHistory => [...prevChatHistory, { message: completeMessage, type: 'api' }]);
                setCurrentAPIMessage(''); // Clear the current API message once done
            })
            .catch(error => {
                console.error("Error sending data:", error);
            });
        } catch (error) {
            console.error("Error sending data:", error);
        }
    };
    const resetAPI = async () => {
        try {
            const response = await apiClient(`openai/chat-ai-reset?session_id=${sessionId}`, 'GET');
            if (response && response.status === "Chat history reset successfully") {
                console.log('Chat session reset successfully.');
            }
        } catch (error) {
            console.error("Error resetting:", error);
        }
    };
    
    const clearHistory = () => {
        setChatHistory([]);
        resetAPI();
    };
    const handleSubmit = (e) => {
        e.preventDefault();
        sendToAPI(input);
        setInput('');
    };
    const chatHistoryRef = React.useRef(null);
    useEffect(() => {
        if (chatHistoryRef.current) {
            chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
        }
    }, [chatHistory, currentAPIMessage]);
    return (
        <div className="container-fluid">
            <h1 className="h3 mb-4 text-gray-800 text-capitalize">Large Language Models (demo)</h1>
            <div className="row justify-content-center">
                <div className="col-lg-8 mb-4"> 
                    <Card>
                        <Card.Header className="bg-primary text-white">
                            <h6 className="m-0 font-weight-bold">Ask Vector Solutions Bot</h6>
                        </Card.Header>
                        <Card.Body className="chat-body p-4"> 
                        <div className="chat-history mb-3" ref={chatHistoryRef}>
                            {chatHistory.map((msgObj, index) => (
                                <div key={index} className={`chat-message ${msgObj.type} p-2 mb-2 rounded`}>
                                    {msgObj.type === 'user' && <i className="fas fa-user-circle mr-2"></i>}
                                    {msgObj.type === 'api' && <i className="fas fa-brain mr-2"></i>}
                                    {msgObj.message}
                                </div>
                            ))}
                            {currentAPIMessage && 
                                <div className={`chat-message api p-2 mb-2 rounded`}>
                                    <i className="fas fa-robot mr-2"></i>
                                    {currentAPIMessage}
                                </div>
                            }
                        </div>
                            <div className="chat-input">
                                <form onSubmit={handleSubmit} className="d-flex">
                                    <div className="input-group">
                                      <div className="input-group-prepend">
                                        <span className="input-group-text">
                                          <i className="fas fa-comment-dots"></i>
                                        </span>
                                      </div>
                                      <input 
                                          className="form-control" 
                                          value={input} 
                                          onChange={e => setInput(e.target.value)} 
                                          placeholder="Type a question..."
                                      />
                                      <div className="input-group-append">
                                        <button 
                                            type="submit" 
                                            className={`btn ${input.trim() ? 'btn-success' : 'btn-secondary'}`}
                                            disabled={!input.trim()}
                                        >
                                            <i className="fas fa-paper-plane"></i> Send
                                        </button>
                                      </div>
                                    </div>
                                </form>
                            </div>
                        </Card.Body>
                        <Card.Footer className="text-right">
                            <button onClick={clearHistory} className="btn btn-danger btn-icon-split">
                                <span className="icon text-white-50">
                                    <i className="fas fa-trash-alt"></i>
                                </span>
                                <span className="text">Clear Chat History</span>
                            </button>                            
                        </Card.Footer>
                    </Card>
                </div>
            </div>
        </div>
    );
}
  
export default LLM;