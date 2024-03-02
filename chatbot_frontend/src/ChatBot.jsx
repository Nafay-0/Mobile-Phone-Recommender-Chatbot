import React, { useState, useRef, useEffect } from "react";
import "./chatbot.css";
import axios from 'axios';
import { ThreeDots } from "react-loader-spinner";
import micOn from './mic-on.svg';
import micOff from './mic-off.svg';

function generateUUID() {
  return crypto.randomUUID();
}

const base64ToBlob = (base64) => {
  const binaryString = window.atob(base64); // Decode base64
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return new Blob([bytes], { type: 'audio/mp3' }); // Assuming the audio is mp3 format
};


function Header({ header, color, fontColor, onToggleMode, mode }) {
  return (
    <div className="header-bot" style={{ backgroundColor: color, color: fontColor }}>
      {header}
      <div className="toggle-switch">
        <button 
          onClick={() => onToggleMode('text')} 
          className={mode === 'text' ? 'active' : ''}
        >
          Text
        </button>
        <button 
          onClick={() => onToggleMode('audio')} 
          className={mode === 'audio' ? 'active' : ''}
        >
          Audio
        </button>
      </div>
    </div>
  );
}

function ChatBotIcon({ image, showChatBot, toggleChatBot }) {
  return (

    <div className={`chatbot-icon ${showChatBot ? 'active' : ''}`} onClick={toggleChatBot}>
      <img src={image} alt="ChatBot Icon" width={60} height={60} />
    </div>

  );
}

function urlify(text) {
  // Regular expression to match URLs. Exclude closing brackets at the end of URLs.
  const urlRegex = /(https?:\/\/[^\s]+?)(?=[,.!?)]*(\s|$))/g;
  return text.replace(urlRegex, (url) => `<a href="${url}" target="_blank">${url}</a>`);
}

// function Input
function Input({ onSend }) {
  const [text, setText] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const handleInputChange = e => {
    setText(e.target.value);
  };

  const handleSend = e => {
    e.preventDefault();
    if (text.trim()) {
      onSend({ type: 'text', content: text });
      setText("");
    }
  };

  const startRecording = async () => {
    try {
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      mediaRecorderRef.current.ondataavailable = (e) => {
        audioChunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.start();

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/mpeg' });
        const audioFile = new File([audioBlob], "recording.mp3", { type: 'audio/mpeg' });

        audioChunksRef.current = [];
        const audioUrl = URL.createObjectURL(audioBlob);

        onSend({ type: 'audio', content: { 'url': audioUrl, 'file': audioFile } });
      };
      setIsRecording(true);

    } catch (error) {
      console.error("Error starting audio recording:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="input">
      <form onSubmit={handleSend}>
        <input
          type="text"
          onChange={handleInputChange}
          value= {isRecording? ' Recording...' : text}
          placeholder="Enter your message here"
        />
        <button type="submit">
          <svg
            version="1.1"
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 500 500"
          >
            <g>
              <g>
                <polygon points="0,497.25 535.5,267.75 0,38.25 0,216.75 382.5,267.75 0,318.75" />
              </g>
            </g>
          </svg>
        </button>

        <button type="button" style={{ top: '0', right: '0' }} onClick={isRecording ? stopRecording : startRecording}>
          {isRecording ? <img src={micOff} width={24} height={24} /> : <img src={micOn} width={24} height={24} />}
        </button>
      </form>
    </div>
  );
}


function BotMessage({ msg, msgColor, fontColor }) {
  const [isLoading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const el = useRef(null);

  useEffect(() => {

    el.current.scrollIntoView({ block: "end", behavior: "smooth" });

  }, [isLoading]);

  useEffect(() => {
    async function loadMessage() {
      setLoading(false);
      setMessage(urlify(msg));
    }
    loadMessage();
  }, [msg]);

  return (
    <div className="message-container-bot">
      <div className="bot-message" style={{ backgroundColor: msgColor, color: fontColor }} dangerouslySetInnerHTML={{ __html: isLoading ? "..." : message }}></div>
      <div ref={el}></div>
    </div>
  );
}

function UserMessage({ text, msgColor, fontColor }) {
  return (
    <div className="message-container">
      <div className="user-message" style={{ backgroundColor: msgColor, color: fontColor }}>{text}</div>
    </div>
  );
}

function AudioMessage({ audioUrl, align, msgColor, fontColor }) {

  const alignmentClass = align === 'left' ? 'message-container-bot' : 'message-container';
  const messageClass = align === 'left' ? 'bot-message' : 'user-message';
  const audioClass = align === 'left' ? 'bot-audio' : 'user-audio';
  const el = useRef(null);

  useEffect(() => {

    if(el.current){
      el.current.scrollIntoView({ block: "end", behavior: "smooth" });
    }
  }, []);


  return (
    <div className={alignmentClass}>
      <div className={messageClass} style={{ backgroundColor: msgColor, color: fontColor, padding: '0' }}>
        <audio controls src={audioUrl} style={{ maxWidth: '100%' }} className={audioClass}>
          Your browser does not support the audio element.
        </audio>
      </div>
      <div ref={el}></div>
    </div>
  );
}


function Messages({ messages, load }) {
  const el = useRef(null);
  useEffect(() => {
    el.current.scrollIntoView({ block: "end", behavior: "smooth" });
  });
  return (
    <div className="messages">
      {messages}
      {load && <div className="loader-style">
        <ThreeDots
          height="50"
          width="50"
          radius="5"
          color="#000000"
          ariaLabel="three-dots-loading"
          wrapperStyle={{}}
          wrapperClassName=""
          visible={true}
        />
      </div>}
      <div id={"el"} ref={el} />
    </div>
  );
}


const fetchMessage = async (type, data, sessionId, responseMode) => {

  try {

    if (type === 'audio') {
      const formData = new FormData();
      formData.append('audio', data);
      formData.append('sessionID', sessionId);
      formData.append('response', responseMode)

      const response = await axios.post('http://localhost:8000/audio-query', formData,{
        "Content-Type": "multipart/form-data",
      },);


      if(responseMode === 'text'){
        return {transcript: 'You said: "'+ response.data.transcript +'"', answer: response.data.answer};
      }
      else if(responseMode === 'audio'){
        const audioBlob = base64ToBlob(response.data.audio);
        const url = URL.createObjectURL(audioBlob);
        return {transcript: 'You said: "'+ response.data.transcript +'"', audio_url: url};
      }
    }

    else {
      const response = await axios.post(`http://localhost:8000/text-query`, {
        question: data,
        sessionID: sessionId,
        response: responseMode,
      });

      if(responseMode === 'text'){
        return response.data.answer;
      }
      else if(responseMode === 'audio'){
        const audioBlob = base64ToBlob(response.data.audio);
        const url = URL.createObjectURL(audioBlob);
        return url
      }
    }

  } catch (error) {

    console.error("Error fetching message:", error);
    return "An error occurred while fetching the message.";
  }

};

function ChatBot({ botID, header, welcomeMessage, headerColor, botMessageColor, userMessageColor, headerFontColor, botFontColor, userFontColor, chatbotIcon }) {
  const [messages, setMessages] = useState([]);
  const [unique, setUnique] = useState(0);
  const [loading, setLoading] = useState(false);
  const [showChatBot, setShowChatBot] = useState(true);
  const [sessionId, setSessionId] = useState('');
  const [mode, setMode] = useState('text'); // Add this state to manage mode

  const toggleMode = (newMode) => {
    setMode(newMode);
  };

  const toggleChatBot = () => {
    setShowChatBot((prevState) => !prevState);
  };

  useEffect(() => {
    async function loadWelcomeMessage() {
      let k = unique;
      setMessages([
        <BotMessage
          key={k}
          msg={welcomeMessage}
          msgColor={botMessageColor}
          fontColor={botFontColor}
        />
      ]);
      k += 1;
      setUnique(k);
    }
    const newSessionId = generateUUID();
    setSessionId(newSessionId);
    loadWelcomeMessage();

  }, []);

  const send = async (message) => {

    let k = unique;

    if (message.type === 'text') {
      let text = message.content;

      const userMessage = <UserMessage key={k} text={text} msgColor={userMessageColor} fontColor={userFontColor} />;
      k += 1;

      setMessages((prevMessages) => [...prevMessages, userMessage]);

      setLoading(true);
      let answer = await fetchMessage('text', text, sessionId, mode);
      setLoading(false);

      if (mode === 'text'){
        const botMessage = (
          <BotMessage
            key={k}
            msg={answer}
            msgColor={botMessageColor}
            fontColor={botFontColor}
          />
        );
  
        setMessages((prevMessages) => [...prevMessages, botMessage]);
      }
      else if (mode === 'audio'){
        const botAudioMessage = <AudioMessage key={k} audioUrl={answer} align={'left'} msgColor={'#f9d9fd'} fontColor={botFontColor} />  
        setMessages((prevMessages) => [...prevMessages, botAudioMessage]);
      }
      
      k += 1;

      setUnique(k);
    }

    else if (message.type === 'audio') {

      let audioUrl = message.content.url;
      let audioFile = message.content.file;
      const audioMessage = <AudioMessage key={k} audioUrl={audioUrl} align={'right'} msgColor={'#b8dafc'} fontColor={userFontColor} />
      k += 1

      setMessages((prevMessages) => [...prevMessages, audioMessage]);

      setLoading(true);
      let response = await fetchMessage('audio', audioFile, sessionId, mode);
      setLoading(false);

      const botMessage1 = (
        <BotMessage
          key={k}
          msg={response.transcript}
          msgColor={botMessageColor}
          fontColor={botFontColor}
        />
      );

      if (mode === 'text'){
        const botMessage2 = (
          <BotMessage
            key={k+1}
            msg={response.answer}
            msgColor={botMessageColor}
            fontColor={botFontColor}
          />
        );
        setMessages((prevMessages) => [...prevMessages, botMessage1, botMessage2]);
      }
      else if(mode === 'audio'){
        const botAudioMessage = <AudioMessage key={k+1} audioUrl={response.audio_url} align={'left'} msgColor={'#f9d9fd'} fontColor={botFontColor} />
        setMessages((prevMessages) => [...prevMessages, botMessage1, botAudioMessage]);
      }
 
      k += 2;

      setUnique(k);
    }

  };


  return (

    <div className="chatbot-container">
      {showChatBot && <div className="chatbot">
        <Header header={header} color={headerColor} fontColor={headerFontColor} onToggleMode={toggleMode} mode={mode} />
        <Messages messages={messages} load={loading} />
        <Input onSend={send} />

      </div>}
      <ChatBotIcon image={chatbotIcon} showChatBot={showChatBot} toggleChatBot={toggleChatBot} />
    </div>
  );
}

export default ChatBot