import React from "react";
import { useEffect, useState } from "react";
import MenuCard from "../components/MenuCard";
import styles from '../styles/Home.module.css'
import url from "../components/url";
import Modal from "../components/Modal";
const Home = () => {
  const [data, setData] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedCardData, setSelectedCardData] = useState(null);

  /********** fetching data here ************/
  const fetchData = () => {
    fetch(`${url}/menu`)
      .then((res) => res.json())
      .then((res) => {
        setData(res);
      })
      .catch((err) => console.log(err));
  };

  const [toggle, setToggle] = useState(false);
 
  useEffect(() => {
    fetchData();
    console.log("data :",data)
  }, [toggle]);

  useEffect(() => {
    console.log("showModal:", showModal);
  }, [showModal]);

  useEffect(() => {
    document.body.classList.toggle("modal-open", showModal);
  }, [showModal]);

  function handleDeleteClick() {
    setToggle(!toggle);
  }
  
  function postUpdatedData(data){
    fetch(`${url}/menu/update/${data.id}`,{
      method:"PUT",
      headers:{
        'Content-type':'application/json',
      },
      body:JSON.stringify(data)
    }).then((res)=>{
      return res.json()
    }).then((res)=>{
      alert(res.msg)
      setToggle(!toggle)
    })
  }

  const handleUpdateClick = (cardData) => {
    setShowModal(true);
    setSelectedCardData(cardData);
    // console.log('cardData ',cardData)
    // console.log(showModal)
  };

  const handleCloseModal = () => {
    setShowModal(false);
  };

  return (
    <>
      {/* <Header
        changeSortFunction={changeSortFunction}
        changeSearchFunction={changeSearchFunction}
      /> */}

      {data === null ? (
        <div className={styles.loding_data}>
          <h1>Loading Data....</h1>
        </div>
      ) : (
        <>
          {data && data.length === 0 ? (
            <div className={styles.loding_data}>
              <h1>No data found....</h1>
            </div>
          ) : (
            <div className={styles.container}>
              {data.map((el, index) => {
                return (
                  <MenuCard
                    key={el.id}
                    data = {el}
                    onDeleteClick={handleDeleteClick}
                    onUpdateClick={handleUpdateClick}
                  />
                );
              })}
              {showModal && (
                <div>
                   <div className="overlay" />
               <Modal
                data={selectedCardData}
                onCloseModal={handleCloseModal}
                onUpdate={(updatedData) => {
                // Handle update logic here, make POST request with updatedData
                console.log('Updated data:', updatedData);
                postUpdatedData(updatedData)
                handleCloseModal();
              }}
              />
               </div>
              )}
             
            </div>
          )}
        </>
      )}
    </>
  );
};

export default Home