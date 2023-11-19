import React from 'react';
import './List.css';
import destination from './images/destination.svg';
import house from './images/house.svg';
import star from './images/star.svg';

const ImageGallery = ({ numberOfImages }) => {
  const images = Array.from({ length: numberOfImages *2}, (_, index) => (
    <img key={index} src={star} width={20} height={20} alt= "ranking"/>
  ));

  return (
      images
  );
};


const List = ({list}) => {

  const listItems = list.map(craftsman => {
    
    const address =  craftsman.street + ' ' + craftsman.house_number + ', '+ craftsman.city
    return <li>
        <div className= 'custom-list'>
            <p>
              <b>{craftsman.name} </b> 
            <p> 
              <img src={destination} width={20} height={20} alt="distance" />
              {' ' + Number((craftsman.dist).toFixed(1)) + ' km '}
              <ImageGallery numberOfImages={craftsman.rankingScore} />
              <br></br>
            <img src={house} width={20} height={20} alt="address" />
              <a href={"https://maps.google.com/?q=" + address} target="_blank" rel="noopener noreferrer">{address}</a>
              </p>
            </p>
      </div>
    </li>
  }
  );

  
  
  return <ul style={mystyle}>{listItems}</ul> ;

};

const mystyle={
    listStyleType:'none'
  }

export default List;
