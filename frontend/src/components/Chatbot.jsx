import React, { useState } from 'react';
import axios from 'axios';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import DotLoader from './DotLoader';
import chatbotImg from '../assets/chatbot.png';
import userImg from '../assets/userIcon.png';
import { FiSend } from 'react-icons/fi';
import { FaTrashAlt } from 'react-icons/fa';

const Chatbot = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [botTyping, setBotTyping] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
  
    const userMessage = { 
      id: Date.now().toString(), 
      role: 'user', 
      content: input, 
      timestamp: new Date().toLocaleTimeString() 
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setBotTyping(true);
  
    try {
      const response = await axios.post('http://localhost:5000/api/chat', { 
        message: input 
      });
  
      // Ensure we're getting the expected response structure
      console.log('API Response:', response.data);
  
      const botMessage = {
        id: Date.now().toString() + '-bot',
        role: 'bot',
        content: response.data?.response || response.data?.message || 'No response',
        tag: response.data?.tag,
        timestamp: new Date().toLocaleTimeString()
      };
  
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('API Error:', error);
      setMessages(prev => [...prev, {
        id: Date.now().toString() + '-error',
        role: 'bot',
        content: error.response?.data?.error || error.message || 'Request failed',
        timestamp: new Date().toLocaleTimeString()
      }]);
    } finally {
      setLoading(false);
      setBotTyping(false);
    }
  };

  return (
    <ChatContainer>
      <ChatHeader>
        <ProfileImage src={chatbotImg} alt="Profile" />
        <HeaderTitle>Sniperbot</HeaderTitle>
        <ClearButton onClick={() => setMessages([])}>
          <FaTrashAlt />
        </ClearButton>
      </ChatHeader>
      <MessageContainer>
        {messages.length === 0 && (
          <DefaultMessage>
            <DefaultImage src={chatbotImg} alt="Chatbot" small />
            <DefaultMessageText>Start chatting with Sniperbot</DefaultMessageText>
          </DefaultMessage>
        )}
        {messages.map((msg) => (
          <Message key={msg.id} role={msg.role} as={motion.div} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            {msg.role === 'bot' && <ProfileImage src={chatbotImg} alt="Chatbot" small />}
            <MessageWrapper role={msg.role}>
              <MessageContent role={msg.role}>{msg.content}</MessageContent>
              <Timestamp>{msg.timestamp}</Timestamp>
            </MessageWrapper>
            {msg.role === 'user' && <ProfileImage src={userImg} alt="User" small />}
          </Message>
        ))}

        {botTyping && (
          <Message role="bot" as={motion.div} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <ProfileImage src={chatbotImg} alt="Chatbot" small />
            <MessageWrapper role="bot">
              <TypingIndicator>
                <TypingText>Bot is typing...</TypingText>
                <DotLoader />
              </TypingIndicator>
            </MessageWrapper>
          </Message>
        )}
      </MessageContainer>
      <MessageInputContainer>
        <MessageInput value={input} onChange={(e) => setInput(e.target.value)} placeholder="Type a message..." />
        <SendButton onClick={sendMessage} as={motion.button} whileTap={{ scale: 0.9 }}>
          <FiSend size={20} />
        </SendButton>
      </MessageInputContainer>
    </ChatContainer>
  );
};

// Styled Components

const MessageContainer = styled.div`
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  max-height: 500px; /* Adjusted to limit the height of the chat */
  
  /* Styling the scrollbar */
  ::-webkit-scrollbar {
    width: 2px; /* Width of the scrollbar */
  }

  ::-webkit-scrollbar-thumb {
    background-color: #888; /* Thumb color */
    border-radius: 10px; /* Rounded corners */
    border: 2px solid #555; /* Optional border around the thumb */
  }

  ::-webkit-scrollbar-track {
    background-color: #f1f1f1; /* Track color */
    border-radius: 10px; /* Rounded corners for the track */
  }

  /* Optional: Styling for hover effect on the scrollbar thumb */
  ::-webkit-scrollbar-thumb:hover {
    background-color: #555; /* Darker thumb color on hover */
  }
`;

const ChatContainer = styled.div`
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 15px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const ChatHeader = styled.div`
  background: #447cf5;
  color: white;
  padding: 15px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const ProfileImage = styled.img`
  width: ${(props) => (props.small ? '30px' : '40px')};
  height: ${(props) => (props.small ? '30px' : '40px')};
  border-radius: 50%;
  margin: ${(props) => (props.small ? '0 10px' : '0')};
`;

const DefaultImage = styled.img`
  width: ${(props) => (props.small ? '100px' : '140px')};
  height: ${(props) => (props.small ? '100px' : '140px')};
  border-radius: 50%;
  margin: ${(props) => (props.small ? '0 10px' : '0')};
`;

const HeaderTitle = styled.h3`
  font-size: 18px;
  flex: 1;
  text-align: center;
`;

const ClearButton = styled.button`
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 16px;
`;

const Message = styled.div`
  margin-bottom: 10px;
  display: flex;
  align-items: flex-end;
  ${(props) => (props.role === 'user' ? 'flex-direction: row-reverse;' : 'flex-direction: row;')}
`;

const MessageWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: ${(props) => (props.role === 'user' ? 'flex-end' : 'flex-start')};
`;

const MessageContent = styled.div`
  background: ${(props) => (props.role === 'user' ? '#447cf5' : '#fff')};
  color: ${(props) => (props.role === 'user' ? 'white' : 'black')};
  padding: 12px;
  border-radius: 12px;
  max-width: 75%;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
`;

const Timestamp = styled.div`
  font-size: 12px;
  color: #666;
  margin-top: 3px;
  text-align: center;
`;

const MessageInputContainer = styled.div`
  display: flex;
  align-items: center;
  padding: 10px;
  background: #fff;
  border-top: 1px solid #ddd;
`;

const MessageInput = styled.input`
  flex: 1;
  padding-top:20px;  
  padding-bottom:20px; 
  padding-left:10px;
  padding-right:10px;
  border: none;
  border-radius: 10px;
  background: #f1f1f1;
  outline: none;
`;

const SendButton = styled.button`
  background: #447cf5;
  color: white;
  border: none;
  padding: 10px;
  margin-left: 10px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const TypingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TypingText = styled.span`
  font-size: 14px;
  color: #666;
`;

const DefaultMessage = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 50px;
  flex-direction: column;
  height:80%;
  text-align: center;
`;

const DefaultMessageText = styled.p`
  font-size: 18px;
  color: #666;
  margin-top: 10px;
`;

export default Chatbot;