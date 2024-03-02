import React, {useState, useEffect} from 'react';
import ChatBot from './ChatBot';
import cicon from './chatbot_icon.png';
import "./chatpage.css";

const text = "DataQuest";

const TextAnimation = () => {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [currentText, setCurrentText] = useState("");

    useEffect(() => {
        const interval = setInterval(() => {
            if (currentText !== text){
            if (currentText.length === text.length) {
                setCurrentText("");
                setCurrentIndex(0);
            } else {
                setCurrentText((prevText) => prevText + text[currentIndex]);
                setCurrentIndex((prevIndex) => (prevIndex + 1) % text.length);
            }
        }
        }, 200); // Change the delay as desired (in milliseconds)

        return () => clearInterval(interval);
    }, [currentText, currentIndex]);

    return (
        <div className="gen-text" >
            {currentText}
            <span className="animate-pulse"></span>
        </div>
    );
};

function App() {
 
    const WelcomeMessage = 'Welcome to DataQuest Mobile Chatbot. How can I help you?'


    return (

        

        <div className="page-container">
            
            <div className='config-container'>
                <TextAnimation/>
             <div className='features'>

                 <h5 className='features-header'>Our Features</h5>
                 <ul className='features-list'>
                     <li>Customized Chatbot for Mobiles</li>
                     <li>Text/Audio Input</li>
                     <li>Name Entity Recognition</li>
                     <li>Accurate Response</li>
                     <li>Interactive UI</li>
                 </ul>

             </div>

            </div>

            <div className='chat-container2'>

            <ChatBot 
                header = {'DataQuest Mobiles'}
                welcomeMessage={WelcomeMessage}
                headerColor={'#000000'}
                botMessageColor={'#312f2f'}
                userMessageColor={'#cccccc'}
                headerFontColor={'#FFFFFF'}
                botFontColor={'#FFFFFF'}
                userFontColor={'#000000'}
                chatbotIcon={cicon} />
            </div>
            
                
        </div>
            
    );
}

export default App;


