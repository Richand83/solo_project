from flask import Flask, redirect, session, render_template, request, redirect,session, flash, url_for
from mysqlconnection import connectToMySQL
app = Flask(__name__)    
app.secret_key = "keep it secret, keep it safe"
from flask_bcrypt import Bcrypt        
bcrypt = Bcrypt(app)
import re

@app.route("/")
def landing_page():

    return render_template("index.html")

#login section & validation
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
@app.route("/register", methods=['POST'])
def add_users():
    is_valid = True
    if len(request.form['fname']) < 1:
        is_valid = False
        flash("Please enter a frist name")
        return redirect("/")
    if len(request.form['lname']) < 1:
        is_valid = False
        flash("Please enter a last name")
        return redirect("/")
    if not EMAIL_REGEX.match(request.form['email']):
        flash('invalid email address')
        return redirect('/')
    if len(request.form['password']) < 1:
        is_valid = False
        flash("Please enter a valid password")
        return redirect("/")
    if request.form['conf_password'] != request.form['password']:
        is_valid = False
        flash("password did not match")
        return redirect("/")
    if is_valid:
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        print(pw_hash)
        mysql = connectToMySQL('team_db')
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(pw)s, NOW(), NOW());"
        data = {
            "fn": request.form["fname"],
            "ln": request.form["lname"],
            "em": request.form["email"],
            "pw": pw_hash
        }
        #store in DB redirect to users page
        mysql.query_db(query,data)
        flash("User successfully added!")
        session['name'] = request.form["fname"]
    return redirect("/" )
@app.route("/forgot_pass")
def update_pass():

    return render_template("forgot_pw.html")

@app.route("/reset_pw")
def reset():
    mysql = connectToMySQL('team_db')
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    query = "UPDATE users SET password = %(new_pw)s WHERE email = %(em)s "
    data = {
        "new_pw": pw_hash,
        "em": request.form['email']
    }
    mysql.query_db(query,data)
if __name__=="__main__":   
    app.run(debug=True) 