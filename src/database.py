from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy.orm import relationship

db = SQLAlchemy()
migrate = Migrate()

class Inventory(db.Model):

    __tablename__ = "inventory"
    model_number = db.Column(db.String(20), primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    available_units = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        data_dict = {}

        for column in self.__table__.columns:
            data_dict[column.name] = getattr(self, column.name)
        return data_dict

    def __repr__(self):
        return f"{self.model_number}_{self.category}"


class Order(db.Model):

    __tablename__ = "order"
    order_number = db.Column(db.String(15), primary_key=True)
    order_item = db.Column(db.String(20), db.ForeignKey("inventory.model_number"))
    order_quantity = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    order_time = db.Column(db.DateTime, default=datetime.now())
    delivery_team_id = db.Column(db.Integer, db.ForeignKey("delivery_team.team_id"))
    delivery_time = db.Column(db.DateTime, nullable=False)
    delivered = db.Column(db.Boolean)
    delivery_team = relationship("DeliveryTeam", back_populates="order")
    delivery_distance = db.Column(db.Float(precision=2), nullable=False)

    def to_dict(self):
        data_dict = {}

        for column in self.__table__.columns:
            data_dict[column.name] = getattr(self, column.name)
        return data_dict


class Customer(db.Model):

    __tablename__ = "customer"
    customer_id = db.Column(db.Integer, primary_key=True, nullable=False)
    customer_name = db.Column(db.String(200), nullable=False)
    order_number = db.Column(db.String(15), db.ForeignKey("order.order_number"))
    customer_address = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        data_dict = {}

        for column in self.__table__.columns:
            data_dict[column.name] = getattr(self, column.name)
        return data_dict

class DeliveryTeam(db.Model):

    __tablename__ = "delivery_team"
    team_id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(20), nullable=False)
    order = relationship("Order", back_populates="delivery_team")
    available_time = db.Column(db.DateTime, default=datetime.now())

    def is_occupied(self):
        if datetime.now() > self.available_time:
            return False
        else:
            return True

    def to_dict(self):
        data_dict = {}

        for column in self.__table__.columns:
            data_dict[column.name] = getattr(self, column.name)
        return data_dict

    def __repr__(self):
        return self.team_name
