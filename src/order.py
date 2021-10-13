from flask import Blueprint, jsonify, request, render_template
from src.database import db, Order, Inventory, Customer, DeliveryTeam
from datetime import datetime, timedelta
from random import choice

order = Blueprint("order", __name__, url_prefix='')
PACKAGING_TIME = timedelta(minutes=20)
HTML_TIME_FORMAT = "%H:%M"


def calculate_new_available_time(available_time, order_time, delivery_distance):
    if available_time > order_time:
        if int(delivery_distance) > 5:
            available_time += timedelta(minutes=80) + PACKAGING_TIME
            delivery_time = available_time - timedelta(minutes=40)
        else:
            available_time += timedelta(minutes=40) + PACKAGING_TIME
            delivery_time = available_time - timedelta(minutes=20)
    else:
        if int(delivery_distance) > 5:
            available_time = order_time + timedelta(minutes=80) + PACKAGING_TIME
            delivery_time = available_time - timedelta(minutes=40)
        else:
            available_time = order_time + timedelta(minutes=40) + PACKAGING_TIME
            delivery_time = available_time - timedelta(minutes=20)

    return available_time, delivery_time


@order.route('/', methods=["POST", "GET"])
def index():
    inventory = db.session.query(Inventory).all()
    inventory_arr = [item.to_dict() for item in inventory]

    teams = [team for team in db.session.query(DeliveryTeam).all()]

    orders = db.session.query(Order).all()
    date_today = datetime.now().date().strftime("%d%m%y")

    # LOGIC FOR ORDER NUMBER

    if orders:

        delivery_team = None

        last_order_number = orders[-1].order_number
        last_order_number_arr = str(last_order_number).split('_')
        last_order_date = last_order_number_arr[0]
        last_serial_number = int(last_order_number_arr[1])

        if last_order_date == date_today:
            new_serial = last_serial_number+1
            last_order_number_arr[1] = f"{new_serial:02d}"
            order_number = '_'.join(last_order_number_arr)
        else:
            new_serial = '01'
            order_number = date_today + '_' + new_serial
            delivery_team = choice(teams)

    else:
        new_serial = '01'
        order_number = date_today+'_'+new_serial
        delivery_team = choice(teams)

    # POST REQUEST
    if request.method == "POST":

        # GET ALL FORM VALUES INCLUDING VALIDATION
        order_item = request.form.get("item")

        try:
            order_quantity = int(request.form.get("quantity"))
        except ValueError:
            return jsonify(error="Enter Valid quantity"), 401

        inventory_item = Inventory.query.filter_by(model_number=order_item).first()
        if int(order_quantity) > inventory_item.available_units:
            return jsonify(error="Not Enough Items for this Unit"), 401

        total_amount = int(request.form.get("price"))

        customer_name = request.form.get("customer_name")

        customer_address = request.form.get("customer_address")

        try:
            delivery_distance = float(request.form.get("distance"))
        except ValueError:
            return jsonify(error="Enter Valid Distance")

        order_time = datetime.now()

        # LOGIC FOR ASSIGNING DELIVERY TEAM

        if not delivery_team:
            team_a = DeliveryTeam.query.filter_by(team_name="Team-A").first()
            team_b = DeliveryTeam.query.filter_by(team_name="Team-B").first()
            if team_a.is_occupied() and not team_b.is_occupied():
                delivery_team = team_b
            elif not team_a.is_occupied() and team_b.is_occupied():
                delivery_team = team_a
            else:
                if team_a.available_time > team_b.available_time:
                    delivery_team = team_b
                else:
                    delivery_team = team_a

        # UPDATING DELIVERY TIME AND TEAM AVAILABILITY TIME
        delivery_team.available_time, delivery_time = calculate_new_available_time(delivery_team.available_time,
                                                                                   order_time,
                                                                                   delivery_distance)
        # COMMIT FOR TEAM TABLE
        db.session.commit()

        # CREATING NEW ORDER
        new_order = Order(order_number=order_number,
                          order_item=order_item,
                          order_quantity=order_quantity,
                          total_amount=total_amount,
                          order_time=order_time,
                          delivery_time=delivery_time,
                          delivered = False,
                          delivery_team_id=delivery_team.team_id,
                          delivery_team=delivery_team,
                          delivery_distance=delivery_distance)
        db.session.add(new_order)
        db.session.commit()
        print(f"Order Placed {new_order.to_dict()}")

        # UPDATING INVENTORY
        inventory_item.available_units -= order_quantity
        db.session.commit()

        # UPDATING CUSTOMER TABLE
        new_customer = Customer(customer_name=customer_name,
                                order_number=new_order.order_number,
                                customer_address=customer_address)
        db.session.add(new_customer)
        db.session.commit()

    return render_template('index.html', order_number=order_number, inventory_arr=inventory_arr)

@order.route("/update_delivery", methods=["POST","GET"])
def update_delivery_time():

    all_orders = Order.query.all()
    orders_info = [order_item.to_dict() for order_item in all_orders]
    if request.method == "POST":
        order_delivered = Order.query.get(request.form.get("order_number"))
        expected_delivery_time = order_delivered.delivery_time
        updated_delivery_time = datetime.combine(datetime.now().date(), datetime.strptime(request.form.get("delivery_time"), HTML_TIME_FORMAT).time())
        time_difference = updated_delivery_time - expected_delivery_time

        order_delivered.delivered = True
        db.session.commit()

        team = order_delivered.delivery_team
        team.available_time += time_difference
        db.session.commit()

        delivery_team_orders = Order.query.filter_by(delivery_team_id=team.team_id).all()
        for orders in delivery_team_orders:
            orders.delivery_time += time_difference
            db.session.commit()

    return render_template('update_delivery.html', orders_info=orders_info)

@order.route('/get_all_orders')
def get_order_numbers():
    all_orders = Order.query.all()
    order_details = [order_item.to_dict() for order_item in all_orders]

    return jsonify(Order_Data=order_details)

@order.route('/inventory')
def check_inventory():
    inventory_array = [inventory_item.to_dict() for inventory_item in Inventory.query.all()]

    return jsonify(Inventory_Data=inventory_array)

@order.route('/order_status/<string:order_number>')
def check_order_status(order_number):
    enquiry_order = Order.query.get(order_number)

    if enquiry_order:
        order_details = enquiry_order.to_dict()
        return jsonify(Status="Order Confirmed", Order_Details=order_details)
    else:
        return jsonify(Warning="No order placed with this ID")

@order.route('/time_of_delivery/<string:order_number>')
def check_estimated_time(order_number):
    enquiry_order = Order.query.get(order_number)

    if enquiry_order:
        order_dict = enquiry_order.to_dict()
        delivery_time = order_dict['delivery_time']
        delivery_status = order_dict['delivered']
        if delivery_status:
            return jsonify(Expected_Delivery_Time=delivery_time, Delivery_Status="Delivered")
        else:
            return jsonify(Expected_Delivery_Time=delivery_time, Delivery_Status="Not Delivered")
    else:
        return jsonify(Warning="No order placed with this ID")
