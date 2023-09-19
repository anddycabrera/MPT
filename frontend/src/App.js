import React from 'react';
import {BrowserRouter, Route, Routes} from "react-router-dom"


import logo from './logo.svg';
import './App.css';
import LLM from './pages/llm';

function App() {
  return (
   <BrowserRouter>
      <Routes>
        <Route path="/" element={<LLM/>} />      
      </Routes>  
   </BrowserRouter>
  );
}

export default App;
