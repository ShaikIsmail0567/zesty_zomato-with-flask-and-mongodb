import React from "react";
import url from "./url";

function MenuCard({
  data,
  onDeleteClick,
  onUpdateClick
}) {


  const handleDeleteButtonClick = (event) => {
    let id = event.target.dataset.id;
    fetch(`${url}/menu/delete/${id}`, {
      method: "DELETE",
      headers: {
        "Content-type": "application/json",
      },
    })
      .then((res) => res.json())
      .then((res) => {
        onDeleteClick();
      })
      .catch((err) => console.log(err));
  };

  const handleUpdateButtonClick = ()=>{
    // console.log("function is ",onUpdateClick)
    onUpdateClick(data)
  }

  return (
  <div className="card" style={{width: "15rem"}}>
    <img className="card-img-top" src={data.image} height={180}  alt={data.name}/>
    <div className="card-body">
      <h5 className="card-title">{data.dish_name}</h5>
      <p className="card-text">Price : {'Rs '+data.price}</p>
      <p className="card-text"> {data.availability =="yes"?"Available":"Not Available"}</p>
      <p className="card-text">Stock: {data.stock}</p>
      <button
        data-id={data.id}
        type="button"
        className="btn btn-danger"
        onClick={handleDeleteButtonClick}
      >
        Delete
      </button>
      <button 
       data-id={data.id}
       type="button" 
       className="btn btn-primary" 
       onClick={handleUpdateButtonClick}
       style={{marginLeft:'5px'}}  
      >
        Update
      </button>
    </div>
  </div>
  );
}

export default MenuCard;

