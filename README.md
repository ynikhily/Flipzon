# Flipzon
HOW TO RUN:<br>
<br>
- Create/Activate a virtual environment for running this project. <br>
- Create .env file under 'Flipzon-master' and add <b>"export SECRET_KEY=flipzon_secret_key"</b>(for windows) OR set "SECRET_KEY=flipzon_secret_key" (for Mac)<br>
- Migrate to the project folder named 'Flipzon-master' on Integrated Development Environment's local terminal or OS Terminal.<br>
- Add the required packages to the activated virtual environments using command: <i>pip install -r requirements.txt</i> <br>
- To start the server run the following command: <i>flask run</i><br>
- To start flask shell run: <i>flask shell</i><br>
- Access the following URLs: <br>
-- Homepage: http://127.0.0.1:5000/<br>
-- Update Delivery: http://127.0.0.1:5000/update_delivery <br>
-- Check Invenntory: http://127.0.0.1:5000/inventory <br>
-- All Orders: http://127.0.0.1:5000/get_all_orders <br>
-- Order Status: http://127.0.0.1:5000/order_status/<order_id> <br>
-- Check Time of Delivery: http://127.0.0.1:5000/time_of_delivery/<order_id> <br>
