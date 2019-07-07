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

#registration section & validation
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
@app.route("/register", methods=['POST'])

# register route

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
    return redirect("/profile" )

# Login route

@app.route("/login", methods=['POST'])
def login():
    mysql = connectToMySQL('team_db')
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = {
        "email": request.form["email"]
    }
    login_info = mysql.query_db(query,data)
    if login_info:
        if bcrypt.check_password_hash(login_info[0]['password'], request.form['password']):
            session['user_id'] = login_info[0]['user_id']
            session['greetings'] = login_info[0]['first_name']
            return redirect('/user_page') #when logging in skip the security questions
    else:
        flash('invalid user name or password')
        return redirect('/')

#log off

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

#set up security when register a new user

@app.route("/profile")
def profile_page():

    return render_template("landing_page.html")

#forgot password route
@app.route("/forgot_pass")
def update_pass():

    return render_template("forgot_pw.html")

@app.route("/security_questions", methods=['POST'])
def security():
    valid_form = False
    if len(request.form['question-one']) > 1:
        valid_form = True
        form_input = request.form['question-one']
    if len(request.form['question-two']) > 1:
        valid_form = True
        form_input = request.form['question-two']
    if len(request.form['question-three']) > 1:
        valid_form = True
        form_input = request.form['question-three']
    if valid_form:
        print(form_input)
        print(session['user_id'])
        mysql = connectToMySQL('team_db')
        query = "UPDATE users SET security_question = %(question)s WHERE user_id = %(u_id)s"
        data = {
            "question": form_input,
            "u_id": session['user_id']
        }
        mysql.query_db(query,data)
        return redirect('/user_page') # when done setting up profile go to users_page

@app.route("/user_page")
def user_page():

    return render_template('user_page.html')

# reset password route

@app.route("/reset_pw", methods=['POST'])
def reset():
    reset_pw = False
    mysql = connectToMySQL('team_db')
    query = "SELECT * FROM users WHERE email = %(em)s"
    data = {"em": request.form['email']}
    user_info = mysql.query_db(query,data)
    if user_info:
        reset_pw = True
        print(reset_pw)
        if reset_pw: #if there is a user returned from prior query get the security question and store it
            mysql = connectToMySQL('team_db')
            query = "SELECT security_question FROM users WHERE email = %(em)s"
            data = {"em": request.form['email']}
            question = mysql.query_db(query,data)
            print(question[0]['security_question'])
            if question[0]['security_question'] != request.form['question-one'] or request.form['question-two'] or request.form['question-three']:
                reset_pw = False
                flash('Security question did not match')
                return redirect('/forgot_pass')
            elif question[0]['security_question'] == request.form['question-one'] or request.form['question-two'] or request.form['question-three']:
                reset_pw = True
                if reset_pw:
                    mysql = connectToMySQL('team_db')
                    pw_hash = bcrypt.generate_password_hash(request.form['password'])
                    query = "UPDATE users SET password = %(new_pw)s WHERE email = %(em)s "
                    data = {
                        "new_pw": pw_hash,
                        "em": request.form['email']
                    }
                    mysql.query_db(query,data)
                    flash('Password Successfully reset!')
                    return redirect('/')


    return redirect('/forgot_pass')
if __name__=="__main__":   
    app.run(debug=True) 