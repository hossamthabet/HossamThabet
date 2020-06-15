import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    users = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = session["user_id"])
    stocks = db.execute("SELECT symbol, SUM(shares) as total_shares, price FROM stocks WHERE id = :user_id GROUP BY symbol",
    user_id = session["user_id"])

    quotes = {}
    for stock in stocks:
        quotes[stock["symbol"]] = lookup(stock["symbol"])
    cash_remaining = users[0]["cash"]
    total = cash_remaining

    return render_template("index.html", quotes=quotes, stocks=stocks, total=total, cash_remaining=cash_remaining)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        #check the symbol exist or not blank
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)
        quote = lookup(request.form.get("symbol"))
        if quote == None:
            return apology("invalid symbol", 400)
        if not request.form.get("shares"):
            return apology("must provide shares", 403)
        # Check if shares was a positive integer
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("shares must be a positive integer", 400)

        # Check if # of shares requested was 0
        if shares <= 0:
            return apology("can't buy less than or 0 shares", 400)


        #check the price of stock & u have money for it
        rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
        price_per_share = quote["price"]
        total_price = price_per_share * shares
        cash_remaining = rows[0]["cash"]
        if total_price > cash_remaining:
            return apology("not enough money")
        # update the cash
        db.execute("UPDATE users SET cash = cash - :price WHERE id = :user_id",
        price=total_price, user_id=session["user_id"])
        #update stocks table (stocks, shares)
        db.execute("INSERT INTO stock (id, symbol, shares, price) VALUES(:user_id, :symbol, :shares, :price)",
        user_id =session["user_id"],
        symbol = request.form.get("shares"),
        shares = shares,
        price = price_per_share)

        flash("Bought!")
        return redirect(url_for("index"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

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
    if request.method == "POST":
        quote = lookup(request.form.get("symbol"))
        if quote == None:
            return apology("invalid symbol", 400)

        return render_template("quoted.html", quote=quote)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        elif not request.form.get("password") == request.form.get("password2"):
            return apology("password doesn't match", 403)
        # Ensure username  doesn't exist
        rows = db.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("username"))

        if len(rows) == 1:
            return apology("the username already exist", 403)
        else:
            username = request.form.get("username")
            password1 = generate_password_hash(request.form.get("password"))
            # Query database for username
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",username, password1)
            # Redirect user to login form
            return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
