from flask import Flask, request, redirect, session, flash, render_template_string
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "digital_vendor_supplier_2026"

DB = "digital_vendor_supplier.db"


# =========================================================
# DATABASE
# =========================================================

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():

    con = db()

    con.executescript("""

    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        address TEXT
    );

    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        unit TEXT NOT NULL,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER NOT NULL,
        supplier_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total REAL NOT NULL,
        status TEXT DEFAULT 'Pending'
    );

    CREATE TABLE IF NOT EXISTS stock(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER NOT NULL,
        item TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS finance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER NOT NULL,
        kind TEXT NOT NULL,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        entry_date TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS business_profiles(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        business_name TEXT, business_type TEXT, category TEXT,
        years_in_business TEXT, business_location TEXT,
        working_days TEXT, working_hours TEXT, raw_materials TEXT,
        purchase_requirement TEXT, preferred_supplier_location TEXT,
        payment_method TEXT, upi_available TEXT, whatsapp TEXT,
        contact_method TEXT
    );

    CREATE TABLE IF NOT EXISTS feedback(
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
        user_type TEXT NOT NULL, rating INTEGER NOT NULL,
        easy_to_use TEXT NOT NULL, useful_feature TEXT NOT NULL,
        improvement TEXT, suggestion TEXT, created_at TEXT NOT NULL
    );

    """)

    # Default Admin

    admin = con.execute(
        "SELECT id FROM users WHERE email=?",
        ("admin@digitalconnect.com",)
    ).fetchone()

    if not admin:

        con.execute("""
        INSERT INTO users
        (name,email,phone,password,role,address)
        VALUES(?,?,?,?,?,?)
        """, (
            "System Admin",
            "admin@digitalconnect.com",
            "9999999999",
            generate_password_hash("admin123"),
            "admin",
            "Mumbai"
        ))

    con.commit()
    con.close()


# =========================================================
# CSS
# =========================================================

CSS = """

*{
    box-sizing:border-box;
}

body{
    margin:0;
    font-family:Arial,Helvetica,sans-serif;
    background:#f3f8f5;
    color:#17352a;
}

a{
    text-decoration:none;
}

.nav{
    height:70px;
    background:white;
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:0 6%;
    box-shadow:0 2px 12px #0001;
}

.logo{
    font-size:21px;
    font-weight:bold;
    color:#087f4f;
}

.nav a{
    margin-left:18px;
    color:#315447;
    font-weight:bold;
}

.btn{
    display:inline-block;
    background:#087f4f;
    color:white;
    padding:11px 17px;
    border-radius:9px;
    border:0;
    font-weight:bold;
    cursor:pointer;
}

.btn:hover{
    background:#06683f;
}

.light{
    background:#e5f5ed;
    color:#087f4f;
}

.danger{
    background:#b42318;
}

.hero{
    padding:85px 8%;
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:45px;
    align-items:center;
    background:linear-gradient(135deg,#e3f8ed,#fff);
}

.hero h1{
    font-size:48px;
    color:#123f30;
    margin:0 0 18px;
}

.hero p{
    font-size:18px;
    line-height:1.7;
    color:#62736c;
}

.hero-card{
    background:#087f4f;
    color:white;
    padding:40px;
    border-radius:25px;
}

.section{
    padding:60px 8%;
}

.title{
    text-align:center;
    margin-bottom:30px;
}

.cards{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:20px;
}

.card,
.panel,
.stat{
    background:white;
    padding:23px;
    border-radius:16px;
    box-shadow:0 7px 25px #0000000d;
}

.card h3{
    color:#087f4f;
}

.card p,
.muted{
    color:#6d7d76;
    line-height:1.6;
}

.footer{
    background:#103c2e;
    color:white;
    text-align:center;
    padding:25px;
}


/* LOGIN / REGISTER */

.auth{
    min-height:100vh;
    display:grid;
    place-items:center;
    background:linear-gradient(135deg,#e4f8ed,#fff);
    padding:25px;
}

.authbox{
    width:min(980px,100%);
    display:grid;
    grid-template-columns:1fr 1fr;
    background:white;
    border-radius:25px;
    overflow:hidden;
    box-shadow:0 20px 60px #0002;
}

.authleft{
    background:linear-gradient(145deg,#087f4f,#0b6546);
    color:white;
    padding:50px;
}

.authleft h1{
    font-size:34px;
}

.authleft p{
    line-height:1.7;
}

.authright{
    padding:45px;
}

label{
    display:block;
    font-weight:bold;
    margin:13px 0 6px;
    color:#315447;
}

input,
select,
textarea{
    width:100%;
    padding:12px;
    border:1px solid #d4e1db;
    border-radius:9px;
    background:#fbfdfc;
}

textarea{
    resize:vertical;
}

.full{
    width:100%!important;
    margin-top:15px;
}

.flash{
    max-width:1100px;
    margin:15px auto;
    padding:13px 18px;
    border-radius:9px;
    font-weight:bold;
}

.success{
    background:#e4f7ed;
    color:#087f4f;
}

.error{
    background:#fdeaea;
    color:#a42323;
}


/* DASHBOARD */

.layout{
    min-height:100vh;
}

.top{
    height:68px;
    background:white;
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:0 4%;
    box-shadow:0 2px 12px #0001;
}

.body{
    display:flex;
    min-height:calc(100vh - 68px);
}

.side{
    width:235px;
    background:#103c2e;
    padding:20px 12px;
}

.side h3{
    color:white;
    padding:10px;
}

.side a{
    display:block;
    color:#dceee7;
    padding:12px;
    border-radius:8px;
    margin:3px 0;
}

.side a:hover{
    background:#087f4f;
}

.main{
    padding:32px;
    flex:1;
}

.stats{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:17px;
    margin:25px 0;
}

.stat small{
    color:#73837c;
}

.stat strong{
    display:block;
    font-size:28px;
    color:#087f4f;
    margin-top:8px;
}

.grid{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:18px;
}

.tablewrap{
    overflow:auto;
}

.table{
    width:100%;
    border-collapse:collapse;
}

.table th,
.table td{
    padding:12px;
    border-bottom:1px solid #e4ece8;
    text-align:left;
}

.table th{
    background:#edf7f2;
}


@media(max-width:800px){

    .hero,
    .authbox{
        grid-template-columns:1fr;
    }

    .cards,
    .grid,
    .stats{
        grid-template-columns:1fr 1fr;
    }

    .side{
        width:190px;
    }
}


@media(max-width:550px){

    .cards,
    .grid,
    .stats{
        grid-template-columns:1fr;
    }

    .body{
        display:block;
    }

    .side{
        width:100%;
    }

    .main{
        padding:20px;
    }

    .hero h1{
        font-size:35px;
    }

    .nav a{
        display:none;
    }
}

"""


# =========================================================
# PAGE FUNCTION
# =========================================================

def page(title, body):

    return render_template_string("""

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>{{ title }}</title>

<style>

{{ css }}

</style>

</head>

<body>

{% with messages = get_flashed_messages(with_categories=true) %}

    {% for category,message in messages %}

        <div class="flash {{ category }}">
            {{ message }}
        </div>

    {% endfor %}

{% endwith %}

{{ body|safe }}

</body>

</html>

""",
    title=title,
    css=CSS,
    body=body
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    body = """

<nav class="nav">

<div class="logo">
🤝 Digital Vendor-Supplier Connect
</div>

<div>
<a href="/">Home</a>
<a href="/login">Login</a>
<a class="btn" href="/register">Register</a>
</div>

</nav>

<section class="hero">

<div>
<span style="display:inline-block;background:#e7f7ef;color:#087f4f;padding:8px 14px;border-radius:20px;font-weight:700;margin-bottom:15px;">
CEP Field Project • Digital Empowerment of Street Vendors
</span>

<h1>
Connecting Street Vendors with Trusted Suppliers
</h1>

<p>
A practical digital platform that helps street vendors discover suppliers,
check products and prices, send purchase requests, manage stock and maintain
basic business information in one place.
</p>

<a class="btn" href="/register">Get Started</a>
<a class="btn light" href="/login">Login</a>

</div>

<div class="hero-card" style="text-align:center;">
<div style="font-size:60px;">🏪 🤝 🏭</div>
<h2>Vendor + Supplier Connect</h2>
<p>
Vendors can find products and suppliers. Suppliers can list products,
receive vendor requests and manage orders.
</p>
<div style="margin-top:18px;padding:14px;background:#f4fbf7;border-radius:12px;font-weight:600;">
Simple • Digital • Practical • Useful
</div>
</div>

</section>

<section class="section">
<div class="title">
<h2>About the Project</h2>
<p>Understanding the purpose of Digital Vendor-Supplier Connect</p>
</div>

<div class="panel" style="max-width:1100px;margin:auto;line-height:1.8;">
<p>
<strong>Digital Vendor-Supplier Connect</strong> is a field-project website based on
<strong>Digital Empowerment of Street Vendors</strong>. The platform is designed to
reduce the difficulty of finding suppliers and managing routine purchasing and
business information digitally.
</p>
<p>
A street vendor can register, maintain a profile, search suppliers, view products,
compare prices, place an order request, manage stock and record sales and expenses.
Suppliers can register their business, add products, view requests and update order
status. An administrator can monitor registered users and orders.
</p>
</div>
</section>

<section class="section" style="background:#f7fbf9;">
<div class="title">
<h2>Project Objectives</h2>
<p>What this platform aims to provide</p>
</div>

<div class="cards">
<div class="card"><h3>📱 Digital Access</h3><p>Provide a simple digital platform for street vendors and suppliers.</p></div>
<div class="card"><h3>🔎 Supplier Discovery</h3><p>Help vendors find supplier details and available products.</p></div>
<div class="card"><h3>💰 Price Awareness</h3><p>Allow vendors to view and compare listed product prices.</p></div>
<div class="card"><h3>📝 Easy Requests</h3><p>Make purchase and order requests easier to send and track.</p></div>
<div class="card"><h3>📦 Stock Management</h3><p>Help vendors maintain basic records of available stock.</p></div>
<div class="card"><h3>📊 Business Records</h3><p>Provide simple sales and expense recording for daily business use.</p></div>
</div>
</section>

<section class="section">
<div class="title">
<h2>Benefits for Street Vendors</h2>
<p>How the website can support everyday business activities</p>
</div>

<div class="cards">
<div class="card"><h3>🏪 Find Suppliers</h3><p>Search supplier information without depending only on manual contacts.</p></div>
<div class="card"><h3>📦 Check Products</h3><p>View product names, categories, prices and available quantities.</p></div>
<div class="card"><h3>💵 Compare Prices</h3><p>View listed prices from available suppliers before sending a request.</p></div>
<div class="card"><h3>🚚 Track Orders</h3><p>Check whether an order request is pending, accepted, rejected or completed.</p></div>
</div>
</section>

<section class="section" style="background:#f7fbf9;">
<div class="title">
<h2>Benefits for Suppliers</h2>
<p>Tools for maintaining products and handling vendor requests</p>
</div>

<div class="cards">
<div class="card"><h3>🏭 Supplier Profile</h3><p>Maintain basic supplier contact and business information.</p></div>
<div class="card"><h3>➕ Add Products</h3><p>List raw materials or products with price and available quantity.</p></div>
<div class="card"><h3>📩 Vendor Requests</h3><p>View requests received from registered street vendors.</p></div>
<div class="card"><h3>✅ Order Management</h3><p>Accept or reject requests and update order status.</p></div>
</div>
</section>

<section class="section">
<div class="title">
<h2>Website Features</h2>
<p>Separate pages are available after login</p>
</div>

<div class="cards">
<div class="card"><h3>🔐 Login & Registration</h3><p>Separate accounts for vendors and suppliers with role-based access.</p></div>
<div class="card"><h3>🔎 Find Suppliers</h3><p>View registered supplier information and contact details.</p></div>
<div class="card"><h3>📦 Products & Raw Materials</h3><p>View supplier products, prices and available quantities.</p></div>
<div class="card"><h3>💰 Price Comparison</h3><p>Compare available product prices listed by suppliers.</p></div>
<div class="card"><h3>📝 Orders</h3><p>Send, accept, reject and track purchase requests.</p></div>
<div class="card"><h3>📊 Stock & Finance</h3><p>Maintain stock records and basic sales and expense entries.</p></div>
<div class="card"><h3>🛡️ Digital Safety</h3><p>Learn basic cyber-safety and safe digital-payment practices.</p></div>
<div class="card"><h3>👨‍💼 Admin Panel</h3><p>Monitor registered users and order information.</p></div>
</div>
</section>

<section class="section" style="background:#f7fbf9;">
<div class="title">
<h2>How It Works</h2>
<p>A simple step-by-step process</p>
</div>

<div class="cards">
<div class="card"><h3>1️⃣ Register</h3><p>Create a Vendor or Supplier account.</p></div>
<div class="card"><h3>2️⃣ Login</h3><p>Open the dashboard according to your account type.</p></div>
<div class="card"><h3>3️⃣ Connect</h3><p>Vendors find suppliers and products; suppliers add their products.</p></div>
<div class="card"><h3>4️⃣ Request</h3><p>Vendor sends an order request with required quantity.</p></div>
<div class="card"><h3>5️⃣ Manage</h3><p>Supplier accepts or rejects the request and updates its status.</p></div>
<div class="card"><h3>6️⃣ Record</h3><p>Vendor can maintain stock, sales and expense information.</p></div>
</div>
</section>

<section class="section">
<div class="title">
<h2>Digital Payment & Cyber Safety</h2>
<p>Important awareness for digital business users</p>
</div>

<div class="cards">
<div class="card">
<h3>💳 Digital Payments</h3>
<p>Use trusted payment applications. Check the receiver name and payment amount before confirming. Never share your UPI PIN or OTP.</p>
</div>
<div class="card">
<h3>🛡️ Cyber Safety</h3>
<p>Use strong passwords, avoid unknown links and never share OTPs, PINs or passwords with another person.</p>
</div>
<div class="card">
<h3>🏛️ Government Information</h3>
<p>For schemes and official benefits, users should verify current information through official government portals.</p>
</div>
</div>
</section>

<section class="section" style="text-align:center;background:#eaf8f1;">
<h2>Ready to Use the Platform?</h2>
<p>Create an account and start using the digital vendor-supplier services.</p>
<a class="btn" href="/register">Create Account</a>
<a class="btn light" href="/login">Login</a>
</section>

<footer class="footer">
Digital Vendor-Supplier Connect
<br>
Digital Empowerment of Street Vendors
<br>
<span style="font-size:13px;">CEP Field Project</span>
</footer>

"""

    return page("Home", body)


# =========================================================

# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()

        email = request.form["email"].strip().lower()

        phone = request.form["phone"].strip()

        password = request.form["password"]

        role = request.form["role"]

        address = request.form.get("address", "").strip()


        if not all([
            name,
            email,
            phone,
            password,
            role
        ]):

            flash(
                "Please fill all required fields.",
                "error"
            )

            return redirect("/register")


        if role not in ["vendor", "supplier"]:

            flash(
                "Select Vendor or Supplier.",
                "error"
            )

            return redirect("/register")


        con = db()

        try:

            con.execute("""

            INSERT INTO users
            (name,email,phone,password,role,address)

            VALUES(?,?,?,?,?,?)

            """, (

                name,
                email,
                phone,
                generate_password_hash(password),
                role,
                address

            ))

            con.commit()

        except sqlite3.IntegrityError:

            con.close()

            flash(
                "Email already registered.",
                "error"
            )

            return redirect("/login")


        con.close()


        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect("/login")


    body = """

<div class="auth">

<div class="authbox">


<div class="authleft">

<div style="font-size:55px">
📝
</div>

<h1>
Create Account
</h1>

<p>
Join vendors and suppliers on one
digital platform.
</p>

<p>
🏪 Street Vendors

<br><br>

🏭 Suppliers

<br><br>

📦 Order Management
</p>

</div>


<div class="authright">

<a href="/">
← Home
</a>

<h2>
Register
</h2>

<form method="POST">


<label>
Full Name
</label>

<input
name="name"
placeholder="Enter your full name"
required
>


<label>
Phone Number
</label>

<input
name="phone"
placeholder="Enter phone number"
required
>


<label>
Email Address
</label>

<input
type="email"
name="email"
placeholder="Enter email"
required
>


<label>
Account Type
</label>

<select
name="role"
required
>

<option value="">
Select Account Type
</option>

<option value="vendor">
Street Vendor
</option>

<option value="supplier">
Supplier
</option>

</select>


<label>
Address
</label>

<textarea
name="address"
rows="3"
placeholder="Enter your address"
></textarea>


<label>
Password
</label>

<input
type="password"
name="password"
placeholder="Minimum 6 characters"
minlength="6"
required
>


<button
class="btn full"
type="submit"
>

Create Account

</button>


</form>


<p>

Already registered?

<a href="/login">
Login
</a>

</p>


</div>

</div>

</div>

"""

    return page("Register", body)


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()

        password = request.form["password"]

        role = request.form["role"].strip().lower()


        con = db()

        user = con.execute(
            """
            SELECT * FROM users
            WHERE LOWER(email)=?
            AND LOWER(role)=?
            """,
            (email, role)
        ).fetchone()

        con.close()


        if user and check_password_hash(
            user["password"],
            password
        ):

            session.clear()

            session["uid"] = user["id"]

            session["name"] = user["name"]

            session["role"] = user["role"]


            return redirect("/dashboard")


        flash(
            "Invalid email, password or account type.",
            "error"
        )


    body = """

<div class="auth">

<div class="authbox">


<div class="authleft">

<div style="font-size:55px">
🤝
</div>

<h1>
Digital Vendor-Supplier Connect
</h1>

<p>
Connect with suppliers,
manage orders and grow digitally.
</p>

<p>
🏪 Vendors

<br><br>

🏭 Suppliers

<br><br>

📦 Order Management
</p>

</div>


<div class="authright">

<a href="/">
← Home
</a>

<h2>
Welcome Back!
</h2>

<p class="muted">
Login to your account
</p>


<form method="POST">


<label>
Login As
</label>

<select
name="role"
required
>

<option value="vendor">
Vendor
</option>

<option value="supplier">
Supplier
</option>

<option value="admin">
Admin
</option>

</select>


<label>
Email Address
</label>

<input
type="email"
name="email"
placeholder="Enter your email"
required
>


<label>
Password
</label>

<input
type="password"
name="password"
placeholder="Enter password"
required
>


<button
class="btn full"
type="submit"
>

Login

</button>


</form>


<p>

Don't have an account?

<a href="/register">
Create Account
</a>

</p>

</div>

</div>

</div>

"""

    return page("Login", body)


# =========================================================
# DASHBOARD REDIRECT
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "uid" not in session:

        return redirect("/login")


    return redirect(
        "/" + session["role"] + "/dashboard"
    )


# =========================================================
# DASHBOARD LAYOUT
# =========================================================

def dashboard_page(
    title,
    links,
    content
):

    menu = ""

    for text, url, icon in links:

        menu += f"""

        <a href="{url}">
        {icon} {text}
        </a>

        """


    body = f"""

<div class="layout">


<div class="top">

<div class="logo">

🤝 Digital Vendor-Supplier Connect

</div>


<div>

<b>
{session.get("name")}
</b>

&nbsp;&nbsp;

<a
class="btn danger"
href="/logout"
>

Logout

</a>

</div>

</div>


<div class="body">


<aside class="side">

<h3>
{title}
</h3>

{menu}

</aside>


<main class="main">

{content}

</main>


</div>


</div>

"""

    return page(title, body)


# =========================================================
# VENDOR DASHBOARD
# =========================================================

@app.route("/vendor/dashboard")
def vendor_dashboard():

    if session.get("role") != "vendor":

        return redirect("/login")


    con = db()

    uid = session["uid"]


    orders = con.execute(
        "SELECT COUNT(*) n FROM orders WHERE vendor_id=?",
        (uid,)
    ).fetchone()["n"]


    stock = con.execute(
        "SELECT COUNT(*) n FROM stock WHERE vendor_id=?",
        (uid,)
    ).fetchone()["n"]


    finance = con.execute("""

    SELECT

    COALESCE(
        SUM(
            CASE
            WHEN kind='Sale'
            THEN amount
            ELSE 0
            END
        ),0
    ) sales,

    COALESCE(
        SUM(
            CASE
            WHEN kind='Expense'
            THEN amount
            ELSE 0
            END
        ),0
    ) expenses

    FROM finance

    WHERE vendor_id=?

    """, (uid,)).fetchone()


    con.close()


    content = f"""

<h1>
Vendor Dashboard
</h1>

<p class="muted">
Welcome, {session["name"]}.
</p>


<div class="stats">


<div class="stat">

<small>
My Orders
</small>

<strong>
{orders}
</strong>

</div>


<div class="stat">

<small>
Stock Items
</small>

<strong>
{stock}
</strong>

</div>


<div class="stat">

<small>
Total Sales
</small>

<strong>
₹{finance["sales"]:.2f}
</strong>

</div>


<div class="stat">

<small>
Expenses
</small>

<strong>
₹{finance["expenses"]:.2f}
</strong>

</div>


</div>


<div class="grid">


<a class="card" href="/profile">

<h3>
👤 My Profile
</h3>

<p>
Update your contact details.
</p>

</a>


<a class="card" href="/vendor/suppliers">

<h3>
🔎 Find Suppliers
</h3>

<p>
View registered suppliers.
</p>

</a>


<a class="card" href="/vendor/products">

<h3>
📦 Products
</h3>

<p>
Browse supplier products.
</p>

</a>


<a class="card" href="/vendor/compare">

<h3>
💰 Price Comparison
</h3>

<p>
Compare product prices.
</p>

</a>


<a class="card" href="/vendor/orders">

<h3>
📝 My Orders
</h3>

<p>
Track your requests.
</p>

</a>


<a class="card" href="/vendor/stock">

<h3>
📊 Stock Management
</h3>

<p>
Maintain stock.
</p>

</a>


<a class="card" href="/vendor/finance">

<h3>
💵 Sales & Expenses
</h3>

<p>
Record business entries.
</p>

</a>


<a class="card" href="/feedback"><h3>⭐ Feedback</h3><p>Share your experience and suggestions.</p></a>

<a class="card" href="/guides">

<h3>
🛡️ Digital Guides
</h3>

<p>
Payments, schemes and cyber safety.
</p>

</a>


</div>

"""


    links = [

        ("Dashboard",
         "/vendor/dashboard",
         "🏠"),

        ("Suppliers",
         "/vendor/suppliers",
         "🔎"),

        ("Products",
         "/vendor/products",
         "📦"),

        ("Orders",
         "/vendor/orders",
         "📝"),

        ("Stock",
         "/vendor/stock",
         "📊"),

        ("Finance",
         "/vendor/finance",
         "💵"),

        ("Profile",
         "/profile",
         "👤"),
        ("Feedback", "/feedback", "⭐")

    ]


    return dashboard_page(
        "Vendor Dashboard",
        links,
        content
    )


# =========================================================
# SUPPLIER DASHBOARD
# =========================================================

@app.route("/supplier/dashboard")
def supplier_dashboard():

    if session.get("role") != "supplier":

        return redirect("/login")


    con = db()

    uid = session["uid"]


    products = con.execute(
        "SELECT COUNT(*) n FROM products WHERE supplier_id=?",
        (uid,)
    ).fetchone()["n"]


    orders = con.execute(
        "SELECT COUNT(*) n FROM orders WHERE supplier_id=?",
        (uid,)
    ).fetchone()["n"]


    pending = con.execute("""

    SELECT COUNT(*) n

    FROM orders

    WHERE supplier_id=?

    AND status='Pending'

    """, (uid,)).fetchone()["n"]


    con.close()


    content = f"""

<h1>
Supplier Dashboard
</h1>

<p class="muted">
Welcome, {session["name"]}.
</p>


<div class="stats">


<div class="stat">

<small>
My Products
</small>

<strong>
{products}
</strong>

</div>


<div class="stat">

<small>
Orders
</small>

<strong>
{orders}
</strong>

</div>


<div class="stat">

<small>
Pending Requests
</small>

<strong>
{pending}
</strong>

</div>


</div>


<div class="grid">


<a class="card" href="/profile">

<h3>
👤 My Profile
</h3>

<p>
Update supplier details.
</p>

</a>


<a class="card" href="/supplier/products">

<h3>
📦 Manage Products
</h3>

<p>
Add products, price and quantity.
</p>

</a>


<a class="card" href="/supplier/orders">

<h3>
📝 Vendor Requests
</h3>

<p>
Accept or reject requests.
</p>

</a>


<a class="card" href="/guides">

<h3>
🛡️ Digital Guides
</h3>

<p>
Payment and safety guidance.
</p>

</a>


</div>

"""


    links = [

        ("Dashboard",
         "/supplier/dashboard",
         "🏠"),

        ("Products",
         "/supplier/products",
         "📦"),

        ("Requests",
         "/supplier/orders",
         "📝"),

        ("Profile",
         "/profile",
         "👤"),
        ("Feedback", "/feedback", "⭐")

    ]


    return dashboard_page(
        "Supplier Dashboard",
        links,
        content
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin/dashboard")
def admin_dashboard():

    if session.get("role") != "admin":

        return redirect("/login")


    con = db()


    users = con.execute(
        "SELECT COUNT(*) n FROM users"
    ).fetchone()["n"]


    vendors = con.execute(
        "SELECT COUNT(*) n FROM users WHERE role='vendor'"
    ).fetchone()["n"]


    suppliers = con.execute(
        "SELECT COUNT(*) n FROM users WHERE role='supplier'"
    ).fetchone()["n"]


    products = con.execute(
        "SELECT COUNT(*) n FROM products"
    ).fetchone()["n"]


    orders = con.execute(
        "SELECT COUNT(*) n FROM orders"
    ).fetchone()["n"]


    con.close()


    content = f"""

<h1>
Admin Dashboard
</h1>

<p class="muted">
Platform overview.
</p>


<div class="stats">


<div class="stat">
<small>Total Users</small>
<strong>{users}</strong>
</div>


<div class="stat">
<small>Vendors</small>
<strong>{vendors}</strong>
</div>


<div class="stat">
<small>Suppliers</small>
<strong>{suppliers}</strong>
</div>


<div class="stat">
<small>Products</small>
<strong>{products}</strong>
</div>


</div>


<div class="grid">


<a class="card" href="/admin/users">

<h3>
👥 Users
</h3>

<p>
View registered accounts.
</p>

</a>


<a class="card" href="/admin/feedback"><h3>⭐ Feedback</h3><p>Review vendor and supplier feedback.</p></a>

<a class="card" href="/admin/orders">

<h3>
📋 Orders
</h3>

<p>
View all orders.
</p>

</a>


</div>

"""


    links = [

        ("Dashboard",
         "/admin/dashboard",
         "🏠"),

        ("Users",
         "/admin/users",
         "👥"),

        ("Orders",
         "/admin/orders",
         "📋"),
        ("Feedback", "/admin/feedback", "⭐")

    ]


    return dashboard_page(
        "Admin Dashboard",
        links,
        content
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "uid" not in session:
        return redirect("/login")

    con = db()
    uid = session["uid"]
    role = session.get("role")

    con.execute("INSERT OR IGNORE INTO business_profiles (user_id) VALUES (?)", (uid,))
    con.commit()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        con.execute("UPDATE users SET name=?, phone=?, address=? WHERE id=?",
                    (name, phone, address, uid))

        if role in ("vendor", "supplier"):
            con.execute("""
            UPDATE business_profiles SET
                business_name=?, business_type=?, category=?, years_in_business=?,
                business_location=?, working_days=?, working_hours=?, raw_materials=?,
                purchase_requirement=?, preferred_supplier_location=?, payment_method=?,
                upi_available=?, whatsapp=?, contact_method=?
            WHERE user_id=?
            """, (
                request.form.get("business_name", "").strip(),
                request.form.get("business_type", "").strip(),
                request.form.get("category", "").strip(),
                request.form.get("years_in_business", "").strip(),
                request.form.get("business_location", "").strip(),
                request.form.get("working_days", "").strip(),
                request.form.get("working_hours", "").strip(),
                request.form.get("raw_materials", "").strip(),
                request.form.get("purchase_requirement", "").strip(),
                request.form.get("preferred_supplier_location", "").strip(),
                request.form.get("payment_method", "").strip(),
                request.form.get("upi_available", "").strip(),
                request.form.get("whatsapp", "").strip(),
                request.form.get("contact_method", "").strip(), uid))

        con.commit()
        session["name"] = name
        flash("Profile updated successfully.", "success")

    user = con.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    business = con.execute("SELECT * FROM business_profiles WHERE user_id=?", (uid,)).fetchone()
    con.close()

    def val(key):
        return business[key] or ""

    if role in ("vendor", "supplier"):
        heading = "Vendor Business Details" if role == "vendor" else "Supplier Business Details"
        extra = f"""
<h3>{heading}</h3>
<label>Business / Stall Name</label>
<input name="business_name" value="{val('business_name')}" placeholder="Enter business name">
<label>Business Type</label>
<input name="business_type" value="{val('business_type')}" placeholder="Food Stall / Grocery / Wholesale">
<label>Product Category</label>
<input name="category" value="{val('category')}" placeholder="Vegetables / Grocery / Food Materials">
<label>Years in Business</label>
<input name="years_in_business" value="{val('years_in_business')}" placeholder="Example: 3 years">
<label>Business Location</label>
<input name="business_location" value="{val('business_location')}" placeholder="Area / Market / Locality">
<label>Working Days</label>
<input name="working_days" value="{val('working_days')}" placeholder="Monday to Saturday">
<label>Working Hours</label>
<input name="working_hours" value="{val('working_hours')}" placeholder="9 AM to 8 PM">
<label>Raw Materials / Products</label>
<textarea name="raw_materials" rows="3" placeholder="List products or materials">{val('raw_materials')}</textarea>
<label>Purchase / Supply Requirement</label>
<textarea name="purchase_requirement" rows="3" placeholder="What do you usually purchase or supply?">{val('purchase_requirement')}</textarea>
<label>Preferred Supplier / Service Location</label>
<input name="preferred_supplier_location" value="{val('preferred_supplier_location')}" placeholder="Powai / Bhandup / Mumbai">
<label>Preferred Payment Method</label>
<select name="payment_method">
<option value="">Select</option>
<option {'selected' if val('payment_method') == 'UPI' else ''}>UPI</option>
<option {'selected' if val('payment_method') == 'Cash' else ''}>Cash</option>
<option {'selected' if val('payment_method') == 'Bank Transfer' else ''}>Bank Transfer</option>
<option {'selected' if val('payment_method') == 'Other' else ''}>Other</option>
</select>
<label>UPI Available</label>
<select name="upi_available">
<option value="">Select</option>
<option {'selected' if val('upi_available') == 'Yes' else ''}>Yes</option>
<option {'selected' if val('upi_available') == 'No' else ''}>No</option>
</select>
<label>WhatsApp Number</label>
<input name="whatsapp" value="{val('whatsapp')}" placeholder="WhatsApp number">
<label>Preferred Contact Method</label>
<input name="contact_method" value="{val('contact_method')}" placeholder="Call / WhatsApp / Email">
"""
    else:
        extra = "<h3>Admin Account</h3><p class='muted'>System administrator profile.</p>"

    body = f"""
<div class="auth"><div class="panel" style="width:min(850px,100%)">
<a href="/dashboard">← Dashboard</a>
<h2>My Profile</h2>
<p class="muted">Keep your personal and business information updated.</p>
<form method="POST">
<label>Full Name</label><input name="name" value="{user['name']}" required>
<label>Email Address</label><input value="{user['email']}" disabled>
<label>Mobile Number</label><input name="phone" value="{user['phone']}" required>
<label>Address</label><textarea name="address" rows="3" placeholder="Full address">{user['address'] or ''}</textarea>
{extra}
<br><br><button class="btn" type="submit">Save Profile</button>
<a class="btn light" href="/dashboard">Cancel</a>
</form></div></div>
"""
    return page("My Profile", body)


# =========================================================
# FIND SUPPLIERS
# =========================================================

@app.route("/vendor/suppliers")
def suppliers():

    if session.get("role") != "vendor":

        return redirect("/login")


    con = db()


    rows = con.execute("""

    SELECT *

    FROM users

    WHERE role='supplier'

    ORDER BY name

    """).fetchall()


    con.close()


    cards = ""


    for row in rows:

        cards += f"""

<div class="card">

<h3>
🏭 {row["name"]}
</h3>

<p>
📞 {row["phone"]}
</p>

<p>
✉️ {row["email"]}
</p>

<p>
📍 {row["address"] or "Not provided"}
</p>

</div>

"""


    if not cards:

        cards = """

<div class="panel">

No suppliers registered yet.

</div>

"""


    return dashboard_page(

        "Find Suppliers",

        [
            ("Dashboard",
             "/vendor/dashboard",
             "🏠"),

            ("Products",
             "/vendor/products",
             "📦")
        ],

        f"""

<h1>
Find Suppliers
</h1>

<div class="grid">

{cards}

</div>

"""

    )


# =========================================================
# VENDOR PRODUCTS
# =========================================================

@app.route("/vendor/products")
def products():

    if session.get("role") != "vendor":

        return redirect("/login")


    con = db()


    rows = con.execute("""

    SELECT

    p.*,

    u.name supplier

    FROM products p

    JOIN users u

    ON p.supplier_id=u.id

    ORDER BY p.name

    """).fetchall()


    con.close()


    cards = ""


    for row in rows:

        cards += f"""

<div class="card">

<h3>
📦 {row["name"]}
</h3>

<p>
Supplier:
{row["supplier"]}
</p>

<p>
Category:
{row["category"]}
</p>

<p>

<b>
₹{row["price"]:.2f}
</b>

/ {row["unit"]}

</p>

<p>
Available:
{row["quantity"]}
{row["unit"]}
</p>


<a
class="btn"
href="/vendor/order/{row["id"]}"
>

Place Request

</a>

</div>

"""


    if not cards:

        cards = """

<div class="panel">

No products available yet.

<br><br>

Ask a supplier to add products.

</div>

"""


    return dashboard_page(

        "Products",

        [
            ("Dashboard",
             "/vendor/dashboard",
             "🏠"),

            ("Compare",
             "/vendor/compare",
             "💰"),

            ("Orders",
             "/vendor/orders",
             "📝")
        ],

        f"""

<h1>
Products / Raw Materials
</h1>

<div class="grid">

{cards}

</div>

"""

    )


# =========================================================
# PRICE COMPARISON
# =========================================================

@app.route("/vendor/compare")
def compare():

    if session.get("role") != "vendor":

        return redirect("/login")


    con = db()


    rows = con.execute("""

    SELECT

    p.*,

    u.name supplier

    FROM products p

    JOIN users u

    ON p.supplier_id=u.id

    ORDER BY p.name,p.price

    """).fetchall()


    con.close()


    table = ""


    for row in rows:

        table += f"""

<tr>

<td>
{row["name"]}
</td>

<td>
{row["supplier"]}
</td>

<td>
{row["category"]}
</td>

<td>
₹{row["price"]:.2f}
</td>

<td>
{row["quantity"]}
{row["unit"]}
</td>

<td>

<a
class="btn"
href="/vendor/order/{row["id"]}"
>

Order

</a>

</td>

</tr>

"""


    if not table:
        table="<tr><td colspan='6'>No products available for comparison yet. Suppliers can add products from their dashboard.</td></tr>"


    return dashboard_page(

        "Price Comparison",

        [
            ("Dashboard",
             "/vendor/dashboard",
             "🏠")
        ],

        f"""

<h1>
Price Comparison
</h1>


<div class="panel tablewrap">

<table class="table">


<tr>

<th>
Product
</th>

<th>
Supplier
</th>

<th>
Category
</th>

<th>
Price
</th>

<th>
Available
</th>

<th>
Action
</th>

</tr>


{table}


</table>

</div>

"""

    )


# =========================================================
# PLACE ORDER
# =========================================================

@app.route(
    "/vendor/order/<int:product_id>",
    methods=["GET", "POST"]
)
def order(product_id):

    if session.get("role") != "vendor":

        return redirect("/login")


    con = db()


    product = con.execute("""

    SELECT *

    FROM products

    WHERE id=?

    """, (product_id,)).fetchone()


    if not product:

        con.close()

        flash(
            "Product not found.",
            "error"
        )

        return redirect("/vendor/products")


    if request.method == "POST":

        quantity = int(
            request.form["quantity"]
        )


        if (
            quantity < 1
            or quantity > product["quantity"]
        ):

            con.close()

            flash(
                "Invalid quantity.",
                "error"
            )

            return redirect(
                f"/vendor/order/{product_id}"
            )


        total = (
            quantity
            * product["price"]
        )


        con.execute("""

        INSERT INTO orders

        (
            vendor_id,
            supplier_id,
            product_id,
            quantity,
            total
        )

        VALUES(?,?,?,?,?)

        """, (

            session["uid"],

            product["supplier_id"],

            product_id,

            quantity,

            total

        ))


        con.commit()

        con.close()


        flash(
            "Order request sent to supplier.",
            "success"
        )


        return redirect(
            "/vendor/orders"
        )


    con.close()


    body = f"""

<div class="auth">

<div class="panel"
style="width:min(600px,100%)">


<a href="/vendor/products">
← Products
</a>


<h2>
Place Order Request
</h2>


<p class="muted">

{product["name"]}

<br>

₹{product["price"]:.2f}
/
{product["unit"]}

<br>

Available:
{product["quantity"]}

</p>


<form method="POST">


<label>
Quantity
</label>


<input
type="number"
name="quantity"
min="1"
max="{product["quantity"]}"
required
>


<br><br>


<button class="btn">
Send Order Request
</button>


</form>


</div>

</div>

"""


    return page(
        "Place Order",
        body
    )


# =========================================================
# VENDOR ORDERS
# =========================================================

@app.route("/vendor/orders")
def vendor_orders():

    if session.get("role") != "vendor":

        return redirect("/login")


    con = db()


    rows = con.execute("""

    SELECT

    o.*,

    p.name product,

    u.name supplier

    FROM orders o

    JOIN products p
    ON o.product_id=p.id

    JOIN users u
    ON o.supplier_id=u.id

    WHERE o.vendor_id=?

    ORDER BY o.id DESC

    """, (
        session["uid"],
    )).fetchall()


    con.close()


    table = ""


    for row in rows:

        table += f"""

<tr>

<td>
#{row["id"]}
</td>

<td>
{row["product"]}
</td>

<td>
{row["supplier"]}
</td>

<td>
{row["quantity"]}
</td>

<td>
₹{row["total"]:.2f}
</td>

<td>
{row["status"]}
</td>

</tr>

"""


    if not table:
        table="<tr><td colspan='6'>No orders yet. Browse Products / Raw Materials to place a request.</td></tr>"


    return dashboard_page(

        "My Orders",

        [
            ("Dashboard",
             "/vendor/dashboard",
             "🏠")
        ],

        f"""

<h1>
My Orders
</h1>


<div class="panel tablewrap">


<table class="table">


<tr>

<th>
ID
</th>

<th>
Product
</th>

<th>
Supplier
</th>

<th>
Quantity
</th>

<th>
Total
</th>

<th>
Status
</th>

</tr>


{table}


</table>


</div>

"""

    )


# =========================================================
# SUPPLIER PRODUCTS
# =========================================================

@app.route(
    "/supplier/products",
    methods=["GET", "POST"]
)
def supplier_products():

    if session.get("role") != "supplier":

        return redirect("/login")


    con = db()


    if request.method == "POST":

        try:

            con.execute("""

            INSERT INTO products

            (
                supplier_id,
                name,
                category,
                price,
                quantity,
                unit,
                description
            )

            VALUES(?,?,?,?,?,?,?)

            """, (

                session["uid"],

                request.form["name"],

                request.form["category"],

                float(
                    request.form["price"]
                ),

                int(
                    request.form["quantity"]
                ),

                request.form["unit"],

                request.form.get(
                    "description",
                    ""
                )

            ))


            con.commit()


            flash(
                "Product added successfully.",
                "success"
            )


        except Exception:

            flash(
                "Please enter valid product details.",
                "error"
            )


    rows = con.execute("""

    SELECT *

    FROM products

    WHERE supplier_id=?

    ORDER BY id DESC

    """, (
        session["uid"],
    )).fetchall()


    con.close()


    table = ""


    for row in rows:

        table += f"""

<tr>

<td>
{row["name"]}
</td>

<td>
₹{row["price"]:.2f}
</td>

<td>
{row["quantity"]}
{row["unit"]}
</td>

</tr>

"""


    body = f"""

<div class="auth">

<div class="panel"
style="width:min(1000px,100%)">


<a href="/supplier/dashboard">
← Dashboard
</a>


<h2>
Manage Products
</h2>


<form method="POST">


<label>
Product Name
</label>

<input
name="name"
placeholder="Cooking Oil"
required
>


<label>
Category
</label>

<input
name="category"
placeholder="Raw Material"
required
>


<label>
Price
</label>

<input
type="number"
step="0.01"
name="price"
required
>


<label>
Quantity
</label>

<input
type="number"
name="quantity"
required
>


<label>
Unit
</label>

<input
name="unit"
placeholder="kg / litre / packet"
required
>


<label>
Description
</label>

<textarea
name="description"
rows="3"
></textarea>


<br><br>


<button class="btn">
Add Product
</button>


</form>


<br>


<h2>
My Products
</h2>


<table class="table">


<tr>

<th>
Product
</th>

<th>
Price
</th>

<th>
Quantity
</th>

</tr>


{table}


</table>


</div>

</div>

"""


    return page(
        "Manage Products",
        body
    )


# =========================================================
# SUPPLIER ORDERS
# =========================================================

@app.route("/supplier/orders")
def supplier_orders():

    if session.get("role") != "supplier":

        return redirect("/login")


    con = db()


    rows = con.execute("""

    SELECT

    o.*,

    p.name product,

    v.name vendor,

    v.phone phone

    FROM orders o

    JOIN products p
    ON o.product_id=p.id

    JOIN users v
    ON o.vendor_id=v.id

    WHERE o.supplier_id=?

    ORDER BY o.id DESC

    """, (
        session["uid"],
    )).fetchall()


    con.close()


    table = ""


    for row in rows:

        if row["status"] == "Pending":

            actions = f"""

<a
class="btn"
href="/supplier/order/{row["id"]}/accept"
>
Accept
</a>

<a
class="btn danger"
href="/supplier/order/{row["id"]}/reject"
>
Reject
</a>

"""

        elif row["status"] == "Accepted":

            actions = f"""

<a
class="btn"
href="/supplier/order/{row["id"]}/deliver"
>
Delivered
</a>

"""

        else:

            actions = "-"


        table += f"""

<tr>

<td>
#{row["id"]}
</td>

<td>
{row["vendor"]}
</td>

<td>
{row["phone"]}
</td>

<td>
{row["product"]}
</td>

<td>
{row["quantity"]}
</td>

<td>
₹{row["total"]:.2f}
</td>

<td>
{row["status"]}
</td>

<td>
{actions}
</td>

</tr>

"""


    if not table:
        table="<tr><td colspan='8'>No vendor requests yet. New vendor orders will appear here.</td></tr>"


    return dashboard_page(

        "Vendor Requests",

        [
            ("Dashboard",
             "/supplier/dashboard",
             "🏠")
        ],

        f"""

<h1>
Vendor Requests
</h1>


<div class="panel tablewrap">


<table class="table">


<tr>

<th>
ID
</th>

<th>
Vendor
</th>

<th>
Phone
</th>

<th>
Product
</th>

<th>
Quantity
</th>

<th>
Total
</th>

<th>
Status
</th>

<th>
Action
</th>

</tr>


{table}


</table>


</div>

"""

    )


# =========================================================
# UPDATE ORDER
# =========================================================

@app.route(
    "/supplier/order/<int:order_id>/<action>"
)
def update_order(
    order_id,
    action
):

    if session.get("role") != "supplier":

        return redirect("/login")


    status = {

        "accept":
        "Accepted",

        "reject":
        "Rejected",

        "deliver":
        "Delivered"

    }.get(action)


    if status:

        con = db()


        con.execute("""

        UPDATE orders

        SET status=?

        WHERE id=?

        AND supplier_id=?

        """, (

            status,

            order_id,

            session["uid"]

        ))


        con.commit()

        con.close()


        flash(
            "Order status updated.",
            "success"
        )


    return redirect(
        "/supplier/orders"
    )


# =========================================================
# STOCK
# =========================================================

@app.route(
    "/vendor/stock",
    methods=["GET", "POST"]
)
def stock():

    if session.get("role") != "vendor":

        return redirect("/login")


    con = db()


    if request.method == "POST":

        con.execute("""

        INSERT INTO stock
        (vendor_id,item,quantity,unit)

        VALUES(?,?,?,?)

        """, (

            session["uid"],

            request.form["item"],

            int(
                request.form["quantity"]
            ),

            request.form["unit"]

        ))


        con.commit()


        flash(
            "Stock saved successfully.",
            "success"
        )


    rows = con.execute("""

    SELECT *

    FROM stock

    WHERE vendor_id=?

    ORDER BY id DESC

    """, (
        session["uid"],
    )).fetchall()


    con.close()


    table = ""


    for row in rows:

        table += f"""

<tr>

<td>
{row["item"]}
</td>

<td>
{row["quantity"]}
</td>

<td>
{row["unit"]}
</td>

</tr>

"""


    body = f"""

<div class="auth">

<div class="panel"
style="width:min(900px,100%)">


<a href="/vendor/dashboard">
← Dashboard
</a>


<h2>
Stock Management
</h2>


<form method="POST">


<label>
Item Name
</label>

<input
name="item"
placeholder="Tomato"
required
>


<label>
Quantity
</label>

<input
type="number"
name="quantity"
required
>


<label>
Unit
</label>

<input
name="unit"
placeholder="kg"
required
>


<br><br>


<button class="btn">
Save Stock
</button>


</form>


<br>


<table class="table">


<tr>

<th>
Item
</th>

<th>
Quantity
</th>

<th>
Unit
</th>

</tr>


{table}


</table>


</div>

</div>

"""


    return page(
        "Stock Management",
        body
    )


# =========================================================
# SALES & EXPENSES
# =========================================================

@app.route(
    "/vendor/finance",
    methods=["GET", "POST"]
)
def finance():

    if session.get("role") != "vendor":

        return redirect("/login")


    con = db()


    if request.method == "POST":

        con.execute("""

        INSERT INTO finance

        (
            vendor_id,
            kind,
            title,
            amount,
            entry_date
        )

        VALUES(?,?,?,?,?)

        """, (

            session["uid"],

            request.form["kind"],

            request.form["title"],

            float(
                request.form["amount"]
            ),

            request.form["entry_date"]

        ))


        con.commit()


        flash(
            "Entry saved successfully.",
            "success"
        )


    rows = con.execute("""

    SELECT *

    FROM finance

    WHERE vendor_id=?

    ORDER BY id DESC

    """, (
        session["uid"],
    )).fetchall()


    summary = con.execute("""

    SELECT

    COALESCE(
        SUM(
            CASE
            WHEN kind='Sale'
            THEN amount
            ELSE 0
            END
        ),0
    ) sales,

    COALESCE(
        SUM(
            CASE
            WHEN kind='Expense'
            THEN amount
            ELSE 0
            END
        ),0
    ) expenses

    FROM finance

    WHERE vendor_id=?

    """, (
        session["uid"],
    )).fetchone()


    con.close()


    table = ""


    for row in rows:

        table += f"""

<tr>

<td>
{row["kind"]}
</td>

<td>
{row["title"]}
</td>

<td>
₹{row["amount"]:.2f}
</td>

<td>
{row["entry_date"]}
</td>

</tr>

"""


    body = f"""

<div class="auth">

<div class="panel"
style="width:min(1000px,100%)">


<a href="/vendor/dashboard">
← Dashboard
</a>


<h2>
Sales & Expenses
</h2>


<p>

Total Sales:

<b>
₹{summary["sales"]:.2f}
</b>

&nbsp;&nbsp;

Total Expenses:

<b>
₹{summary["expenses"]:.2f}
</b>

</p>


<form method="POST">


<label>
Type
</label>

<select name="kind">

<option>
Sale
</option>

<option>
Expense
</option>

</select>


<label>
Title
</label>

<input
name="title"
placeholder="Daily sales / Raw material"
required
>


<label>
Amount
</label>

<input
type="number"
step="0.01"
name="amount"
required
>


<label>
Date
</label>

<input
type="date"
name="entry_date"
required
>


<br><br>


<button class="btn">
Save Entry
</button>


</form>


<br>


<table class="table">


<tr>

<th>
Type
</th>

<th>
Title
</th>

<th>
Amount
</th>

<th>
Date
</th>

</tr>


{table}


</table>


</div>

</div>

"""


    return page(
        "Sales and Expenses",
        body
    )


# =========================================================
# DIGITAL GUIDES
# =========================================================

@app.route("/guides")
def guides():

    if "uid" not in session:

        return redirect("/login")


    body = """

<div class="auth">

<div class="panel"
style="width:min(1000px,100%)">


<a href="/dashboard">
← Dashboard
</a>


<h2>
Digital Awareness & Guides
</h2>


<div class="cards">


<div class="card">

<h3>
💳 Digital Payments
</h3>

<p>

Use trusted payment applications.

Always check the receiver name.

Never share your UPI PIN or OTP.

</p>

</div>


<div class="card">

<h3>
🛡️ Cyber Safety
</h3>

<p>

Use strong passwords.

Avoid unknown links.

Never share OTP, PIN or password.

</p>

</div>


<div class="card">

<h3>
🏛️ Government Schemes
</h3>

<p>

Check official government portals
for current street-vendor schemes
and eligibility information.

</p>

</div>


</div>


</div>

</div>

"""


    return page(
        "Digital Guides",
        body
    )


# =========================================================
# FEEDBACK
# =========================================================

@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if "uid" not in session:
        return redirect("/login")

    if request.method == "POST":
        try:
            rating=int(request.form.get("rating", "0"))
            easy=request.form.get("easy_to_use", "").strip()
            useful=request.form.get("useful_feature", "").strip()
            if rating not in (1,2,3,4,5) or not easy or not useful:
                raise ValueError
            con=db()
            con.execute("""
            INSERT INTO feedback
            (user_id,user_type,rating,easy_to_use,useful_feature,improvement,suggestion,created_at)
            VALUES(?,?,?,?,?,?,?,?)
            """, (session["uid"],session.get("role",""),rating,easy,useful,
                   request.form.get("improvement", "").strip(),
                   request.form.get("suggestion", "").strip(),
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            con.commit(); con.close()
            flash("Thank you! Your feedback was submitted successfully.", "success")
            return redirect("/feedback")
        except Exception:
            flash("Please complete the required feedback fields.", "error")

    body="""
<div class="auth"><div class="panel" style="width:min(750px,100%)">
<a href="/dashboard">← Dashboard</a>
<h2>⭐ Website Feedback</h2>
<p class="muted">Your feedback helps improve the platform.</p>
<form method="POST">
<label>Rating</label><select name="rating" required><option value="">Select</option><option value="5">5 - Excellent</option><option value="4">4 - Very Good</option><option value="3">3 - Good</option><option value="2">2 - Needs Improvement</option><option value="1">1 - Poor</option></select>
<label>Was the website easy to use?</label><select name="easy_to_use" required><option value="">Select</option><option>Yes</option><option>Somewhat</option><option>No</option></select>
<label>Which feature was most useful?</label><select name="useful_feature" required><option value="">Select feature</option><option>Supplier Search</option><option>Products / Raw Materials</option><option>Price Comparison</option><option>Orders</option><option>Stock Management</option><option>Sales & Expenses</option><option>Business Profile</option><option>Digital Guides</option></select>
<label>What can be improved?</label><textarea name="improvement" rows="3"></textarea>
<label>Suggestions</label><textarea name="suggestion" rows="4"></textarea>
<br><br><button class="btn" type="submit">Submit Feedback</button>
</form></div></div>
"""
    return page("Feedback", body)


# =========================================================
# ADMIN FEEDBACK
# =========================================================

@app.route("/admin/feedback")
def admin_feedback():
    if session.get("role") != "admin":
        return redirect("/login")
    con=db()
    rows=con.execute("""
    SELECT f.*,u.name,u.email FROM feedback f
    JOIN users u ON f.user_id=u.id ORDER BY f.id DESC
    """).fetchall()
    con.close()
    table="".join(f"<tr><td>#{r['id']}</td><td>{r['name']}</td><td>{r['user_type'].title()}</td><td>{r['rating']}/5</td><td>{r['easy_to_use']}</td><td>{r['useful_feature']}</td><td>{r['improvement'] or '-'}</td><td>{r['suggestion'] or '-'}</td><td>{r['created_at']}</td></tr>" for r in rows)
    if not table:
        table="<tr><td colspan='9'>No feedback submitted yet.</td></tr>"
    return dashboard_page("Feedback",[("Dashboard","/admin/dashboard","🏠"),("Users","/admin/users","👥"),("Orders","/admin/orders","📋")],f"""
<h1>Website Feedback</h1><p class="muted">Review feedback submitted by vendors and suppliers.</p>
<div class="panel tablewrap"><table class="table"><tr><th>ID</th><th>Name</th><th>Type</th><th>Rating</th><th>Easy?</th><th>Useful Feature</th><th>Improvement</th><th>Suggestion</th><th>Date</th></tr>{table}</table></div>
""")


# =========================================================
# ADMIN USERS
# =========================================================

@app.route("/admin/users")
def admin_users():

    if session.get("role") != "admin":

        return redirect("/login")


    con = db()


    rows = con.execute("""

    SELECT *

    FROM users

    ORDER BY id DESC

    """).fetchall()


    con.close()


    table = ""


    for row in rows:

        table += f"""

<tr>

<td>
{row["id"]}
</td>

<td>
{row["name"]}
</td>

<td>
{row["email"]}
</td>

<td>
{row["phone"]}
</td>

<td>
{row["role"]}
</td>

<td>
{row["address"] or "-"}
</td>

</tr>

"""


    return dashboard_page(

        "Admin Users",

        [
            ("Dashboard",
             "/admin/dashboard",
             "🏠")
        ],

        f"""

<h1>
Registered Users
</h1>


<div class="panel tablewrap">


<table class="table">


<tr>

<th>
ID
</th>

<th>
Name
</th>

<th>
Email
</th>

<th>
Phone
</th>

<th>
Role
</th>

<th>
Address
</th>

</tr>


{table}


</table>


</div>

"""

    )


# =========================================================
# ADMIN ORDERS
# =========================================================

@app.route("/admin/orders")
def admin_orders():

    if session.get("role") != "admin":

        return redirect("/login")


    con = db()


    rows = con.execute("""

    SELECT

    o.*,

    p.name product,

    v.name vendor,

    s.name supplier

    FROM orders o

    JOIN products p
    ON o.product_id=p.id

    JOIN users v
    ON o.vendor_id=v.id

    JOIN users s
    ON o.supplier_id=s.id

    ORDER BY o.id DESC

    """).fetchall()


    con.close()


    table = ""


    for row in rows:

        table += f"""

<tr>

<td>
#{row["id"]}
</td>

<td>
{row["vendor"]}
</td>

<td>
{row["supplier"]}
</td>

<td>
{row["product"]}
</td>

<td>
{row["quantity"]}
</td>

<td>
₹{row["total"]:.2f}
</td>

<td>
{row["status"]}
</td>

</tr>

"""


    return dashboard_page(

        "Admin Orders",

        [
            ("Dashboard",
             "/admin/dashboard",
             "🏠")
        ],

        f"""

<h1>
All Orders
</h1>


<div class="panel tablewrap">


<table class="table">


<tr>

<th>
ID
</th>

<th>
Vendor
</th>

<th>
Supplier
</th>

<th>
Product
</th>

<th>
Quantity
</th>

<th>
Total
</th>

<th>
Status
</th>

</tr>


{table}


</table>


</div>

"""

    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect("/")


# =========================================================
# START
# =========================================================

init_db()


if __name__ == "__main__":

    app.run(
        debug=True
    )