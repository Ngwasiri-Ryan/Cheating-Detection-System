import React, { useState, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';

const DotLoader = () => {
  return (
    <Container>
      <Dot delay="0s" />
      <Dot delay="0.2s" />
      <Dot delay="0.4s" />
    </Container>
  );
};

const bounce = keyframes`
  0% { transform: translateY(0); opacity: 0.3; }
  50% { transform: translateY(-5px); opacity: 1; }
  100% { transform: translateY(0); opacity: 0.3; }
`;

const Container = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
`;

const Dot = styled.div`
  width: 8px;
  height: 8px;
  margin: 0 5px;
  border-radius: 50%;
  background-color: #447cf5;
  animation: ${bounce} 1.2s infinite ease-in-out;
  animation-delay: ${(props) => props.delay};
`;

export default DotLoader;