import logo from './images/check24_logo.svg';
import './App.css';
import React, { useState, useEffect} from 'react';
import List from './List.js'
import './List.css';



function App() {

  const [showList, setShowList] = useState(false);
  const [list, setList] = useState([]);
  const [currentPostcode, setCurrentPostcode] = useState("")
  const [currentIndex, setCurrentIndex] = useState(0)
  const [showLoadMoreButton, setShowLoadMoreButton] = useState(true);

  const handleInput = (e) => {
    setCurrentPostcode(e.target.value)
  }

  useEffect(() => {
    const intervalId = setInterval(async () => {

      if(showList) {
        // Perform fetch request here
        // For example, fetching data every 5 minutes
        const response = await fetch('http://localhost:1234/craftsmen?postalcode=' + currentPostcode);
        const result = await response.json();
        console.error("a")
        setList(result.craftsmen);
        console.error(result.craftsmen)
        if (result.craftsmen.length < 20) {
          setShowLoadMoreButton(false);
        }
      }
    },  5 * 60 * 1000); // 5 minutes in milliseconds

    // Cleanup the interval when the component unmounts
    return () => clearInterval(intervalId);
  }, [showList, currentPostcode]); // Run the effect whenever currentPostcode changes


  const handleButtonClick = async () => {
    setShowLoadMoreButton(true)
    try {
      const response = await fetch('http://localhost:1234/craftsmen?postalcode=' + currentPostcode);
      
      if (response.status === 400) {
        // Handle the case where postal code is not found
        console.error('Postal code not found');
        alert("Postal code not found. Please enter a valid postal code.")
        return;
      }

      const result = await response.json();
      setList(result.craftsmen);
      if (result.craftsmen.length < 20) {
        setShowLoadMoreButton(false); // Hide the button if there are no more items
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
      // Toggle the visibility of the list
    setShowList(true);
    setCurrentIndex(0);
  };


  const handleLoadMore = async (e)=> {
    const c = currentIndex + list.length;
    try {
      const response = await fetch('http://localhost:1234/craftsmen?postalcode=' + currentPostcode + "&index=" + c);
      const result = await response.json();
      setList((list) => list.concat([...result.craftsmen]));
      if (result.craftsmen.length < 20) {
        setShowLoadMoreButton(false); // Hide the button if there are no more items
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setCurrentIndex(currentIndex + list.length)
  };

  return (
    <div className="App">
      <div className="banner">
      <img src={logo} alt="check24 logo"/>
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
        <>
        < List list={list} />
        {showLoadMoreButton && <button onClick={handleLoadMore}>Load More</button>}
        </>
        )
        }
      </div>
    </div>
  );
}

export default App;

