from flask import Flask, request, jsonify, json
from flask_cors import CORS
from pymongo import MongoClient


app = Flask(__name__)

CORS(app)

client = MongoClient('mongodb+srv://ismail:ismail@cluster0.vzy7h1u.mongodb.net/flask_zomato?retryWrites=true&w=majority')

db = client['zesty_zomato']
collection = db['menu-data']

class MenuManager:
    def __init__(self, menu_file):
        self.menu_file = menu_file
        self.menu_data = self.load_menu_from_file()

    def load_menu_from_file(self):
        with open(self.menu_file, 'r') as file:
            menu_data = json.load(file)
        return menu_data

    def save_menu_to_file(self):
        with open(self.menu_file, 'w') as file:
            json.dump(self.menu_data, file,indent=3)

    def add_dish(self, dish):
        self.menu_data.append(dish)
        self.save_menu_to_file()

    def remove_dish(self, dish_id):
        dish_found = False
        for dish in self.menu_data:
            if dish['id'] == dish_id:
                dish_found = True
                self.menu_data.remove(dish)
                self.save_menu_to_file()
                return {'msg':'dish deleted!','deleted_dish':{**dish}}
        if not dish_found:
            return {"msg":"dish not found!"}

    def update_dish_availability(self, dish_id, updated_dish):
        dish_found = False
        for dish in self.menu_data:
            if dish['id'] == dish_id:
                dish_found = True
                dish['dish_name'] = updated_dish['dish_name']
                dish['price'] = updated_dish['price']
                dish['availability'] = updated_dish['availability']
                dish['stock'] = updated_dish['stock']
                dish['image'] = updated_dish['image']

                self.save_menu_to_file()
                return {'msg':"dish updated!",'updated_dish':{**dish}}
        if not dish_found:
            return {"msg":"dish not found!"}

    def get_menu(self):
        return self.menu_data


# Order managemnt is here...
class OrderManager:
    def __init__(self,orders_file) -> None:
        self.orders_file = orders_file
        self.orders = self.load_orders_from_file()
        self.order_id_count = self.get_next_order_id_from_file()
    
    # load order from file
    def load_orders_from_file(self):
        try:
            with open(self.orders_file,"r") as file:
               return json.load(file)
        except FileNotFoundError:
            return []
    
    # save orders to file
    def save_orders_to_file(self):
        with open(self.orders_file,'w') as file:
            json.dump(self.orders,file,indent=3)

    # get current order count form count file
    @staticmethod
    def get_next_order_id_from_file():
        with open("./count.txt",'r') as file:
            try:
               content =  file.read()
               curr_count = int(content.split("=")[1].strip())
               return curr_count
            except FileNotFoundError:
               return 1


    def get_next_order_id(self):
        order_id = self.order_id_count
        self.order_id_count += 1
        with open("./count.txt",'w') as file:
            file.write(f'count = {self.order_id_count}')
        return order_id

    def record_order(self, customer_name, dish_id, quantity, menu_manager):
        dish_found = False
        dish_to_remove = []
        for dish in menu_manager.menu_data:
            if dish['id'] == dish_id:
                dish_found  = True
                if dish['availability'] == "yes":
                    if dish['stock'] >= quantity:
                        dish['stock'] -= quantity
                        order = {
                           'customer_name': customer_name,
                           'order_id':self.get_next_order_id(),
                           'quantity': quantity,
                           'total_price':quantity * dish['price'],
                           'status': 'received'
                        }
                        self.orders.append(order)

                        self.save_orders_to_file()
                        
                        menu_manager.save_menu_to_file() #saving again after duducting the stock
                        if dish['stock'] == 0:
                           dish_to_remove.append(dish)
                        return {'msg':"Order Placed!",'order':order}
                    else:
                        return {'msg':"Insufficient Stock!"}
                else:
                    return {'msg':'Dish is not available!'}
        # remove the dish with 0 stock
        for dish in dish_to_remove:
            menu_manager.menu_data.remove(dish)
        menu_manager.save_menu_to_file()        
        if not dish_found:
            return {'msg':'Dish not found in the menu_data!'}

            
    def see_all_orders(self):
        return self.orders

    def change_order_status(self,order_id,status):
        order_found = False
        for order in self.orders:
            if order['order_id'] == order_id:
                order_found = True
                order['status'] = status
                self.save_orders_to_file()
                return {'msg':'order status changed!','order':order}

        if not order_found:
            return {'msg':'No orders found!'}
            
    # filter based on order status
    def filter_based_on_order(self,status):
        filtered_data = [order for order in self.orders if order['status'] == status ]
        return filtered_data




# creating an instance of MenuManager and sending file name as argument
menu_manager = MenuManager('menu.json')
order_manager = OrderManager('orders.json')



# check if mongoDB connected
try:
    # Access a collection to check the connection
    count = collection.count_documents({})
    print(f"MongoDB connected. Collection count: {count}")
except ConnectionError as e:
    print(f"Failed to connect to MongoDB. Error: {str(e)}")


# get all the dish data
@app.route('/menu', methods=['GET'])
def get_menu():
    documents = collection.find()

# add dish
@app.route('/menu/add', methods=['POST'])
def add_dish():
    dish = request.json
     # Validate dish data
    if 'dish_name' not in dish or 'price' not in dish or 'availability' not in dish or 'stock' not in dish or 'image' not in dish:
        return jsonify({"msg": "Please prived all fields!"}), 400

    # Insert the dish data into the MongoDB collection
    inserted_dish = collection.insert_one(dish)
    return jsonify({"msg":"dish added successfully","dish":dish})



# update dish availabilty
@app.route("/menu/update/<int:id>",methods=['PUT'])
def update_availability(id):
    updated_dish = request.json
    response =  menu_manager.update_dish_availability(id,updated_dish)
    return jsonify(response)



# delete one of the dish
@app.route('/menu/delete/<int:id>',methods=['DELETE'])
def delete_dish(id):
    response =  menu_manager.remove_dish(id)
    return jsonify(response)


# get all orders route
@app.route("/orders",methods=['GET'])
def orders():
   orders =  order_manager.see_all_orders()
   return orders

# add order route
@app.route("/orders/add/<int:id>",methods=['POST'])
def add_order(id):
    customer_name = request.json['customer_name']
    quantity = request.json['quantity']
    response =  order_manager.record_order(customer_name,id,quantity,menu_manager)
    return jsonify(response)


# update the status of a order route
@app.route("/orders/update/<int:id>",methods=['PUT'])
def change_status(id):
    if 'status' not in request.json:
        return {'msg':'Please enter a status of the order!'}
    status = request.json['status'].lower()
    if status not in ['received', 'preparing','ready for pickup','delivered']:
        return {'msg':'Please enter valid status!'}
    
    response = order_manager.change_order_status(id,status)
    return jsonify(response)



# filter based on status route
@app.route("/orders/<string:status>",methods=['GET'])
def filter_order(status):
    if status not in ['received', 'preparing','ready for pickup','delivered']:
        return {'msg':'Please enter valid status!'}
    filtered_orders = order_manager.filter_based_on_order(status)
    return jsonify(filtered_orders)



if __name__ == '__main__':
    app.run(port=4000, debug=True)