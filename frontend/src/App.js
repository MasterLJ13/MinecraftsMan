import logo from './images/check24_logo.svg';
import './App.css';
import React, { useState } from 'react';
import List from './List.js'
import { craftsman } from './data.js';
import './List.css';



function App() {

  const [showList, setShowList] = useState(false);
  const [list, setList] = useState([craftsman]);
  const [currentPostcode, setCurrentPostcode] = useState("")

  const handleInput = (e) => {
    setCurrentPostcode(e.target.value)
  } 

  const handleButtonClick = async () => {

    try {
      const response = await fetch('https://localhost:1234/craftsmen' + '?' + "postalcode=" + currentPostcode);
      const result = await response.json();
      console.log(result)
      setList(result);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
      // Toggle the visibility of the list
    setShowList(true);
  };

  return (
    <div className="App">
      <div className="banner">
      <img src={logo} />
      </div>
      <div className="banner2">
      <h1>Discover Craftsmanship, Find Quality.</h1>
      </div>
      <div className="content">
        <h2>Search for Craftsman</h2>
        <input type="text" 
          id="search" 
          placeholder="What is your Post Code?" 
          pattern="[0-9]*" 
          maxLength = {5}
          onChange = {handleInput} 
          />
        <button onClick={handleButtonClick}>Search</button>
        {showList &&  (
        < List list={list} /> 
        )
        }
      </div>
    </div>
  );
}

export default App;

