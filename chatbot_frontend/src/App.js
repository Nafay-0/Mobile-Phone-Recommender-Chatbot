import React from 'react';
import ChatBot from './ChatBot';
import cicon from './chatbot_icon.png';

function App() {
 
    const WelcomeMessage = 'Welcome to DataQuest Mobile Chatbot. How can I help you?'


    return (
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
    );
}

export default App;


