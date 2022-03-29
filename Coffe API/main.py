
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
from random import choice

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']="TopSecretAPIKey"
Bootstrap(app)
db = SQLAlchemy(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

class CafeForm(FlaskForm):
    name=StringField('Cafe name',validators=[DataRequired()])
    map_url = StringField('Url mapa', validators=[DataRequired(), URL()])
    img_url = StringField("Url image", validators=[DataRequired(),URL()])
    loc= StringField("Location",validators=[DataRequired()])
    seats = StringField("Seats",validators=[DataRequired()])
    toilet = SelectField("Has toilet",choices=["true","false"],validators=[DataRequired()])
    wifi= SelectField("Has wifi",choices=["true","false"],validators=[DataRequired()])
    sockets = SelectField("Has sockets",choices=["true","false"],validators=[DataRequired()])
    calls = SelectField("Can take calls",choices=["true","false"],validators=[DataRequired()])
    coffee_price = StringField("Coffe price",validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route("/")
def home():
    return render_template("index.html")
    

@app.route("/random",methods=["GET"])
def get_random_cafe():
    cafe=db.session.query(Cafe).all()
    random_cafe=choice(cafe)

    return jsonify(cafe=random_cafe.to_dict())

@app.route("/all",methods=["GET"])
def all():
    cafes=db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

@app.route("/search",methods=["GET"])
def def_cafe_at_location():
    query_location=request.args.get("loc")
    cafe=db.session.query(Cafe).filter_by(location=query_location).first()

    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not found":"Ups, we don't have a cafe at that location."})

@app.route("/add",methods=["POST","GET"])
def add_new_cafe():
    form=CafeForm()
    if form.validate_on_submit():
        new_cafe=Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("loc"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success":"Succesfully added the new cafe."})
    return render_template("add.html",form=form)

@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."})
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})

@app.route("/delete_cafe/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

if __name__ == '__main__':
    app.run(debug=True)
