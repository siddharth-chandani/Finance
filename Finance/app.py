import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """ Show portfolio of stocks """
    try:
        userid = session["user_id"]
        user_d = db.execute("SELECT * from users where id =?", userid)
        user_cash = user_d[0]["cash"]
        trans_d = db.execute("SELECT * from transactions where userid = ?", userid)
        return render_template("index.html", cash=user_cash, trans_d=trans_d)
    except IndexError:
        return redirect("/login")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        # Returning apology if the symbol is empty or doesn't exists
        if (not symbol) or (not lookup(symbol)):
            return apology("Invalid symbol")
        # Returning apology if the no. of shares is negative
        elif shares < 0:
            return apology("Please enter a positive number of shares")

        d_s = lookup(symbol)
        userid = session["user_id"]
        d_u = db.execute("SELECT * FROM users WHERE id = ? ", userid)

        # Returning apology if user can't afford given no. of shares
        if shares * d_s["price"] > d_u[0]["cash"]:
            return apology("Insufficient Balance")

        # updating user's cash after buying stocks
        updated_cash = d_u[0]["cash"] - (shares * d_s["price"])
        db.execute("UPDATE users SET cash = ? where id = ?", updated_cash, userid)

        # Now inserting a new row into Transactions table
        date = datetime.datetime.now()
        db.execute("INSERT INTO transactions (userid,symbol,price,shares,comp_name,date) VALUES (?,?,?,?,?,?)",
                   userid, symbol, d_s["price"], shares, d_s["name"], date)

        # Now inserting a new row into history table
        db.execute("INSERT INTO history (userid,symbol,shares,price,transacted) VALUES (?,?,?,?,?)",
                   userid, symbol, shares, d_s["price"], date)

        flash("BOUGHT!")

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    try:
        userid = session["user_id"]
        his_d = db.execute("SELECT * from history WHERE userid = ?", userid)
        return render_template("history.html", his_d=his_d)
    except:
        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # rendering to quote.html if user uses get method
    if request.method == 'GET':
        return render_template("quote.html")

    # else if the user uses post method:
    # then rendering price and name of company to quoted.html
    d = lookup(request.form.get("symbol"))
    # returning apology if symbol doesn't exists
    if not d:
        return apology("INVALID SYMBOL")
    else:
        return render_template("quoted.html", price=usd(d["price"]), comp_name=d["name"], symbol=d["symbol"])


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username ")
        # Checking if Username is already existing or not
        elif db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username")):
            return apology("username already exists")

         # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password",)
        # Checking if confirmation password and original password both are same
        elif not (request.form.get("password") == request.form.get("confirmation")):
            return apology("Incorrect password")

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")))

        return redirect("/")

     # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        userid = session["user_id"]
        trans_d = db.execute("SELECT * from transactions where userid =?", userid)
        return render_template("sell.html", trans_d=trans_d)
    else:
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        userid = session["user_id"]
        trans_d = db.execute("SELECT * from transactions where userid =?", userid)
        user_d = db.execute("SELECT * from users where id = ?", userid)

        if symbol == None:
            return apology("MISSING SYMBOL")
        elif shares < 0:
            return apology("ENTER A POSITIVE NO. OF SHARES")
        error = 1
        for trans in trans_d:
            if trans["symbol"] == symbol:
                if trans["shares"] >= shares:
                    updated_shares = trans["shares"]-shares
                    price = trans["price"]
                    error = 0
        if error == 1:
            return apology("TOO MANY SHARES ")

        # updating user's cash
        updated_cash = user_d[0]["cash"]+(shares*price)
        db.execute("UPDATE users SET cash = ? where id = ?", updated_cash, userid)

        # updating no. of shares
        if updated_shares == 0:
            db.execute("DELETE FROM transactions where symbol = ?", symbol)
        else:
            db.execute("UPDATE transactions SET shares = ? where symbol = ?", updated_shares, symbol)

        # Now inserting a new row into history table
        date = datetime.datetime.now()
        db.execute("INSERT INTO history (userid,symbol,shares,price,transacted) VALUES (?,?,?,?,?)",
                   userid, symbol, -shares, price, date)

        flash("SOLD!")

        # Redirect user to home page
        return redirect("/")



@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Changing User's Password """

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":


        old=request.form.get("old_password")
        new=request.form.get("new_password")
        userid=session["user_id"]
        u_d=db.execute("SELECT * FROM users WHERE id = ?", userid)
        # Ensure old password was submitted
        if not old:
            return apology("must provide old password ")

        # Checking if given old password is correct or not

        elif not check_password_hash(u_d[0]["hash"],old):
            return apology("Password incorrect")

         # Ensure new password was submitted
        elif not new:
            return apology("must provide new password",)
        # Checking if confirmation password and original password both are same
        elif not (new == request.form.get("confirm_password")):
            return apology("Incorrect password")

        db.execute("UPDATE users set hash =? WHERE id =?", generate_password_hash(new),userid)

        flash("Password Changed !!")

        return redirect("/")

     # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("password.html")
