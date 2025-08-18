import os
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableList

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
db = SQLAlchemy()
 
login_manager = LoginManager(app)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable=False)
    password = db.Column(db.String(250),
                         nullable=False)
    queries = db.Column(db.Text,
                         nullable=False, default="")
    bills = db.Column(MutableList.as_mutable(db.JSON),
              default=[False, False, False, False])
    booked = db.Column(db.Boolean, default=False, nullable=False)
 
 
db.init_app(app)
 
with app.app_context():
    db.create_all()

@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)

@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":
        if not db.session.query(Users).filter_by(username=request.form.get("uname")).count() < 1:
            return render_template("register.html", value = "This user already exists!")
        
        if request.files['file'].filename == '':
            return render_template("register.html", value = "Please upload a ID proof in order to continue!")
        user = Users(username=request.form.get("uname"),
                     password=request.form.get("psw"))
        
        db.session.add(user)    
        db.session.commit()
    
    
        return redirect(url_for("login"))

    return render_template("register.html", value ="")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))


    if request.method == "POST":
        user = Users.query.filter_by(
            username=request.form.get("uname")).first()
        if not user:
            return render_template("login.html", value = "This user does not exist!")
    
    
        if user.password == request.form.get("psw"):
            login_user(user)
            return redirect(url_for("index"))
        else:
            return render_template("login.html", value="Incorrect password!")
    return render_template("login.html", value="", uname="")

@app.route("/aboutprez")
def aboutprez():
    return render_template("aboutprez.html")

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    return render_template("profile.html", name = current_user.username, queries = current_user.queries)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/query", methods=["GET", "POST"])
def query():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    if request.method == "POST":
        current_user.queries = current_user.queries + f'''
            <div class="billgridrow">
                <div class="billgridcolumn">
                    <div class="billrect">
                        <p>{request.form.get("type")}</p>
                    </div>
                </div>
                <div class="billgridcolumn">
                    <div class="billrect">
                        <p>Unresolved</p>
                    </div>
                </div>
                <div class="billgridcolumn">
                    <div class="queryrect">
                        <p>{request.form.get("name")}</p>
                    </div>
                </div>
            </div>
        '''
        db.session.commit()
        return redirect(url_for("profile"))
    return render_template("query.html")

@app.route("/bill", methods=["GET", "POST"])
def bill():
    n = request.args.get("n")
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    if request.method == "POST":
        current_user.bills[int(n)] = True
        db.session.commit()
        return redirect(url_for("profile"))
    return render_template("bill.html")

@app.route("/book", methods=["GET", "POST"])
def book():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    if request.method == "POST":
        current_user.booked = True
        db.session.commit()
        return redirect(url_for("profile"))
    return render_template("book.html")

if __name__ == "__main__":
    app.run(host ="0.0.0.0", port = 10000, debug=True   )