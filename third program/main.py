import os
from bson import ObjectId
from django.forms import FloatField
from flask import Flask, jsonify, render_template, request, redirect, flash, session, url_for
from pymongo import MongoClient
from cryptography.fernet import Fernet
from mongoengine import connect, Q, Document, StringField, ListField, IntField, EmbeddedDocument, EmbeddedDocumentField, FloatField
import random
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Connect to MongoDB
connect('House', host='localhost', port=27017)

client = MongoClient('mongodb://localhost:27017/')
db = client['House']
adm = db['householder']
renroom = db['householder']
room = db['room']
contact_msg = db['contact_message']
usr = db['user']

UPLOAD_FOLDER = os.path.join('static', 'img', 'created')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# def generate_key():
#     key = Fernet.generate_key()
#     return key

key = b'9EHlNyRMJ3240yzUFIcUfc3tizfj8cb2EM1ZRbr8Fk4='
fernet = Fernet(key)

def encrypt_password(password):
    return fernet.encrypt(password.encode()).decode()  # Store as a string

def decrypt_password(encrypted_password):
    return fernet.decrypt(encrypted_password.encode()).decode()

class Post(Document):
    fullname = StringField(required=True, max_length=50)
    email = StringField(required=True, max_length=70)
    username = StringField(required=True, max_length=50)
    password = StringField(required=True, max_length=50)
    profile_image = StringField()  # Field to store profile image URL

class Address(EmbeddedDocument):
    House_no = StringField(required=True)
    street = StringField(required=True)
    vill_city = StringField(required=True)
    district = StringField(required=True)
    state = StringField(required=True)
    pin_code = StringField(required=True)

class Room(Document):
    room_name = StringField(required=True)
    location = StringField(required=True)
    room_for = StringField(required=True)
    price = IntField(required=True)
    description = StringField(required=True)
    images = ListField(StringField())  # List to store image URLs
    username = StringField(required=True)  # Associate room with the user
    address = EmbeddedDocumentField(Address)
    deposit = FloatField(required=True)
    leaseDuration = IntField(required=True)
    utilities = StringField(required=True)
    bedrooms = IntField(required=True)
    bathrooms = IntField(required=True)
    parking = StringField(required=True)
    contactName = StringField(required=True)
    contactEmail = StringField(required=True)
    contactPhone = StringField(required=True)
    favorite = StringField()
    request = StringField()
    requested_by = StringField()

@app.route("/Admin_login", methods=['GET', 'POST'])
def Admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = adm.find_one({'username': username})
        if user:
            encrypted_password = user['password']
            try:
                decrypted = decrypt_password(encrypted_password)

                if decrypted == password:
                    session['user'] = username
                    return redirect(url_for('Admin_home'))
                else:
                    flash("Invalid username or password", "error")
            except Exception as e:
                flash("An error occurred during decryption. Please try again.", "error")
        else:
            flash("Invalid username or password", "error")
    return render_template("Admin_login.html")

@app.route("/User_login", methods=['GET', 'POST'])
def User_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Fetch user data from the 'usr' collection
        user = usr.find_one({'username': username})
        if user:
            encrypted_password = user['password']
            try:
                decrypted = decrypt_password(encrypted_password)
                # Check decrypted password with user input
                if decrypted == password:
                    session['user_id'] = str(user['_id'])  # Store user ID
                    session['user'] = username  # Store username
                    session['fullname'] = user.get('fullname', 'N/A')  # Ensure fullname is stored
                    session['email'] = user.get('email', 'unknown@example.com')  # Ensure email is stored
                    flash("Login successful!", "success")
                    return redirect(url_for('User_home'))
                else:
                    flash("Invalid username or password", "error")
            except Exception as e:
                flash("An error occurred during decryption. Please try again.", "error")
        else:
            flash("Invalid username or password", "error")

    return render_template("User_login.html")

otp_storage = {}

def send_otp(email):
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    print(otp)  # For debugging purposes, remove in production

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        from_email = 'samkurre62682@gmail.com'
        server.login(from_email, 'mony nnfa nahn pdxn')  # Use environment variables for production
        msg = EmailMessage()
        msg['Subject'] = "OTP Verification"
        msg['From'] = from_email
        msg['To'] = email
        msg.set_content("The One Time Password (OTP) to verify your Email Address given in Registration form for Home Renter. Please do not share this code with anyone. \n" + "Email OTP is : " + otp)

        server.send_message(msg)
        server.quit()
        return otp
    except Exception as e:
        print(f"Error sending email: {e}")
        return None

@app.route("/Admin_register", methods=['GET', 'POST'])
def Admin_register():
    if request.method == 'POST':
        if 'send_otp' in request.form:
            email = request.form.get('email')
            if email:
                otp = send_otp(email)
                if otp:
                    otp_storage[email] = otp  # Store the OTP
                    session['email'] = email  # Store the email in session
                    flash("OTP sent! Please check your email.", "success")
                    return render_template("Admin_register.html", show_otp=True)  # Show OTP input field
                else:
                    flash("Failed to send OTP. Please try again.", "error")
            else:
                flash("Email is required.", "error")
        
        elif 'verify_otp' in request.form:
            fullname = request.form.get('fullname')
            username = request.form.get('username')
            password = request.form.get('password')
            OTP = request.form.get('otp')
            user_email = session.get('email')

            if not fullname or not user_email or not username or not password:
                flash("All fields are required.", "error")
                return render_template("Admin_register.html", show_otp=True, 
                                       fullname=fullname, username=username, password=password, email=user_email)

            if adm.find_one({'username': username}):
                flash('username already exists', 'info')
                return render_template("Admin_register.html", show_otp=True, 
                                       fullname=fullname, username=username, password=password, email=user_email)

            # Verify OTP
            if user_email in otp_storage and otp_storage[user_email] == OTP:
                flash("OTP Verified! You can now register.", "success")
                session['otp_verified'] = True  # Set the OTP verified session variable
                del otp_storage[user_email]  # Remove the OTP after verification
                return render_template("Admin_register.html", show_otp=False, 
                                       fullname=fullname, username=username, password=password, email=user_email)
            else:
                flash("Wrong OTP. Please verify your email address.", "error")
                return render_template("Admin_register.html", show_otp=True, 
                                       fullname=fullname, username=username, password=password, email=user_email)

    # Keep the previous values in case of GET request or validation failure
    fullname = request.form.get('fullname', '')
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    email = session.get('email', '')

    return render_template("Admin_register.html", show_otp=False, 
                           fullname=fullname, username=username, password=password, email=email)

@app.route("/register_admin", methods=['POST'])
def register_admin():
    fullname = request.form.get('fullname')
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    en_password = encrypt_password(password)
    # Save user to the database (implement this)
    adm.insert_one({'fullname': fullname, 'username': username, 'password': en_password, 'email': email, 'profile_image': '/static/img/download.png'})

    flash("Registration successful!", "success")
    return redirect(url_for('Admin_login'))

@app.route("/register_user", methods=['POST'])
def register_user():
    fullname = request.form.get('fullname')
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    en_password = encrypt_password(password)
    # Save user to the database (implement this)
    usr.insert_one({'fullname': fullname, 'username': username, 'password': en_password, 'email': email})

    flash("Registration successful!", "success")
    return redirect(url_for('User_login'))

@app.route("/upload_profile_picture_for_admin", methods=['POST'])
def upload_profile_picture_for_admin():
    if 'file' not in request.files:
        flash("No file part", "error")
        return redirect(url_for('Admin_home'))

    file = request.files['file']
    if file.filename == '':
        flash("No file selected", "error")
        return redirect(url_for('Admin_home'))

    username = session.get('user')
    if username:
        # Save the file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Update the user's profile image in the database
        image_url = url_for('static', filename=f'img/created/{file.filename}')
        adm.update_one({'username': username}, {'$set': {'profile_image': image_url}})

        flash("Profile picture uploaded successfully!", "success")
        return redirect(url_for('Admin_home'))

    flash("User not logged in", "error")
    return redirect(url_for('Admin_home'))

@app.route("/upload_profile_picture_for_user", methods=['POST'])
def upload_profile_picture_for_user():
    if 'file' not in request.files:
        flash("No file part", "error")
        return redirect(url_for('User_home'))

    file = request.files['file']
    if file.filename == '':
        flash("No file selected", "error")
        return redirect(url_for('User_home'))

    username = session.get('user')
    if username:
        # Save the file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Update the user's profile image in the database
        image_url = url_for('static', filename=f'img/created/{file.filename}')
        usr.update_one({'username': username}, {'$set': {'profile_image': image_url}})

        flash("Profile picture uploaded successfully!", "success")
        return redirect(url_for('User_home'))

    flash("User not logged in", "error")
    return redirect(url_for('User_home'))

@app.route("/Update_home_detail/<string:room_id>", methods=['GET', 'POST'])
def Update_home_detail(room_id):
    if "user" in session:
        user = adm.find_one({'username': session['user']})
        if user:
            profile_image = user.get('profile_image', 'img/admin_img.png')  # Default image if not found
            
            if request.method == 'POST':
                # Get form data
                room_name = request.form['room_name']
                room_for = request.form['room_for']
                House_no = request.form['House_no']
                street = request.form['street']
                vill_city = request.form['vill_city']
                district = request.form['district']
                state = request.form['state']
                pin_code = request.form['pin_code']
                price = request.form['price']
                deposit = request.form['deposit']
                leaseDuration = request.form['leaseDuration']
                utilities = request.form['utilities']
                bedrooms = request.form['bedrooms']
                bathrooms = request.form['bathrooms']
                parking = request.form['parking']
                contactName = request.form['contactName']
                contactEmail = request.form['contactEmail']
                contactPhone = request.form['contactPhone']
                location = request.form['location']
                description = request.form['description']
                images = request.files.getlist('images')

                # Prepare the list of new image URLs
                new_image_urls = []
                for img in images:
                    if img and img.filename:
                        img_path = os.path.join(UPLOAD_FOLDER, img.filename)
                        img.save(img_path)  # Save the image
                        image_url = url_for('static', filename=f'img/created/{img.filename}')
                        new_image_urls.append(image_url)

                # Fetch existing room data
                existing_room = Room.objects(id=ObjectId(room_id), username=session['user']).first()
                if existing_room:
                    # Get existing images
                    existing_image_urls = existing_room.images or []

                    # Append new images to existing images
                    updated_image_urls = existing_image_urls + new_image_urls

                    # Update the room with the new data
                    existing_room.update(
                        room_name=room_name,
                        room_for=room_for,
                        address={
                            "House_no": House_no,
                            "street": street,
                            "vill_city": vill_city,
                            "district": district,
                            "state": state,
                            "pin_code": pin_code
                        },
                        price=price,
                        deposit=deposit,
                        leaseDuration=leaseDuration,
                        utilities=utilities,
                        bedrooms=bedrooms,
                        bathrooms=bathrooms,
                        parking=parking,
                        contactName=contactName,
                        contactEmail=contactEmail,
                        contactPhone=contactPhone,
                        location=location,
                        description=description,
                        images=updated_image_urls  # Save the updated image URLs
                    )
                    flash("Room updated successfully!", "success")
                    return redirect(url_for('Update_home_detail', room_id=room_id))
                else:
                    flash("Room not found or you do not have permission to update this room", "error")
                    return redirect(url_for('Admin_home'))

            # For GET requests, fetch room details
            room_details = Room.objects(id=ObjectId(room_id), username=session['user']).first()
            if room_details:
                return render_template('Update_home_detail.html', room=room_details, profile_image=profile_image)
            else:
                flash("Room not found or you do not have permission to view this room", "error")
                return redirect(url_for('Admin_home'))
        else:
            return redirect(url_for('Admin_home'))
    else:
        return redirect(url_for('Admin_login'))
    
@app.route("/full_detail_of_room/<string:room_id>")
def full_detail_of_room(room_id):
    if 'user' in session:
        user = adm.find_one({'username': session['user']})
        if user:
            # Filter rooms by the logged-in user
            room = Room.objects(id=ObjectId(room_id)).first()
            return render_template('full_detail_of_room.html', username=user['username'], room=room, room_id=room_id, profile_image=user.get('profile_image', 'img/admin_img.png'))
    else:
        return render_template('Admin_home.html')

@app.route("/full_detail/<string:room_id>")
def full_detail(room_id):
    room = Room.objects(id=ObjectId(room_id)).first()
    return render_template('full_detail.html', room = room, room_id = room_id)

@app.route("/")
def Home():
    rooms = Room.objects()
    room_type = Room.objects(room_for='family')
    state = Room.objects(address__state='Chhattisgarh')  # Fetch all room documents
    return render_template('Home.html', rooms=rooms, room_type = room_type, state = state)

@app.route("/User_home")
def User_home():
  
    if 'user' in session:
        user = usr.find_one({'username' : session['user']})
        if user:
            rooms = Room.objects()
            room_type = Room.objects(room_for='family')
            state = Room.objects(address__state = 'Chhattisgarh')
            return render_template('User_home.html', rooms=rooms, room_type=room_type, state=state, profile_image=user.get('profile_image', 'img/admin_img.png'),
                                   username=user['username'])

@app.route("/User_register", methods=['GET', 'POST'])
def User_register():
    if request.method == 'POST':
        if 'send_otp' in request.form:
            email = request.form.get('email')
            if email:
                otp = send_otp(email)
                if otp:
                    otp_storage[email] = otp  # Store the OTP
                    session['email'] = email  # Store the email in session
                    flash("OTP sent! Please check your email.", "success")
                    return render_template("User_register.html", show_otp=True)  # Show OTP input field
                else:
                    flash("Failed to send OTP. Please try again.", "error")
            else:
                flash("Email is required.", "error")
        
        elif 'verify_otp' in request.form:
            fullname = request.form.get('fullname')
            username = request.form.get('username')
            password = request.form.get('password')
            OTP = request.form.get('otp')
            user_email = session.get('email')

            if not fullname or not user_email or not username or not password:
                flash("All fields are required.", "error")
                return render_template("User_register.html", show_otp=True, 
                                       fullname=fullname, username=username, password=password, email=user_email)

            if usr.find_one({'username': username}):
                flash('username already exists', 'info')
                return render_template("User_register.html", show_otp=True, 
                                       fullname=fullname, username=username, password=password, email=user_email)

            # Verify OTP
            if user_email in otp_storage and otp_storage[user_email] == OTP:
                flash("OTP Verified! You can now register.", "success")
                session['otp_verified'] = True  # Set the OTP verified session variable
                del otp_storage[user_email]  # Remove the OTP after verification
                return render_template("User_register.html", show_otp=False, 
                                       fullname=fullname, username=username, password=password, email=user_email)
            else:
                flash("Wrong OTP. Please verify your email address.", "error")
                return render_template("User_register.html", show_otp=True, 
                                       fullname=fullname, username=username, password=password, email=user_email)

    # Keep the previous values in case of GET request or validation failure
    fullname = request.form.get('fullname', '')
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    email = session.get('email', '')

    return render_template("User_register.html", show_otp=False, 
                           fullname=fullname, username=username, password=password, email=email)

@app.route("/searched_home", methods=['GET', 'POST'])
def searched_home():
    rooms = []
    if request.method == 'POST':
        search_query = request.form.get('query')
        rooms = Room.objects( Q(room_name__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(room_for__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(utilities__icontains=search_query))
    return render_template('searched_home.html', rooms = rooms)

@app.route("/Admin_home")
def Admin_home():
    if 'user' in session:
        user = adm.find_one({'username': session['user']})
        if user:
            # Filter rooms by the logged-in user
            rooms = Room.objects(username=session['user'])
            return render_template('Admin_home.html', username=user['username'], rooms=rooms, profile_image=user.get('profile_image', 'img/admin_img.png'))
        else:
            return redirect(url_for('Admin_login'))
    else:
        return redirect(url_for('Admin_login'))
                   
@app.route("/Add_home_detail", methods=['GET', 'POST'])
def Add_home_detail():
    if 'user' in session:
        user = adm.find_one({'username': session['user']})
        if user:
            if request.method == 'POST':
                room_name = request.form.get('room_name')
                location = request.form.get('location')
                room_for = request.form.get('room_for')
                price = request.form.get('price')
                description = request.form.get('description')
                House_no = request.form.get('House_no')
                street = request.form.get('street')
                vill_city = request.form.get('vill_city')
                district = request.form.get('district')
                state = request.form.get('state')
                pin_code = request.form.get('pin_code')
                deposit = request.form.get('deposit')
                leaseDuration = request.form.get('leaseDuration')
                utilities = request.form.get('utilities')
                bedrooms = request.form.get('bedrooms')
                bathrooms = request.form.get('bathrooms')
                parking = request.form.get('parking')
                contactName = request.form.get('contactName')
                contactEmail = request.form.get('contactEmail')
                contactPhone = request.form.get('contactPhone')
                images = request.files.getlist('images')
                image_urls = []

                for image in images:
                    if image and image.filename != '':
                        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
                        image.save(image_path)
                        image_url = url_for('static', filename=f'img/created/{image.filename}')
                        image_urls.append(image_url)

                # Create address object
                address = Address(
                    House_no=int(House_no),
                    street=street,
                    vill_city=vill_city,
                    district=district,
                    state=state,
                    pin_code=pin_code
                )

                # Create and save the new room
                new_room = Room(
                    room_name=room_name,
                    location=location,
                    room_for=room_for,
                    price=price,
                    description=description,
                    address=address,
                    deposit=deposit,
                    leaseDuration=leaseDuration,
                    utilities=utilities,
                    bedrooms=bedrooms,
                    bathrooms=bathrooms,
                    parking=parking,
                    contactName=contactName,
                    contactEmail=contactEmail,
                    contactPhone=contactPhone,
                    images=image_urls,
                    username=session['user']  # Associate room with the logged-in user
                )

                new_room.save()  # Use save method to insert the new Room document
                flash('Room added successfully!', 'success')
                return redirect(url_for('Admin_home'))
            else:
                return render_template('Add_home_detail.html', username=user['username'], profile_image=user.get('profile_image', 'img/admin_img.png'))
        else:
            flash("User not found", "error")
            return redirect(url_for('Admin_login'))
    else:
        flash("You need to be logged in to access this page", "error")
        return redirect(url_for('Admin_login'))

@app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        user = adm.find_one({'username': username})

        if user:
            return redirect(url_for('show_credentials', username=user['username']))
        else:
            flash('username not found', 'error')

    return render_template("forgot_password.html")

@app.route("/show_credentials")
def show_credentials():
    username = request.args.get('username')
    user = adm.find_one({'username': username})
    if user:
        decrypted_password = decrypt_password(user['password'])
        user['password'] = decrypted_password 
        return render_template("show_credentials.html", post=user)  # 'post' is defined here
    else:
        flash('User not found', 'error')
        return redirect(url_for('Admin_login'))

@app.route('/admin_logout')
def admin_logout():
    session.pop('user', None)
    return redirect(url_for('Admin_login'))

@app.route("/frontpage")
def frontpage():
    return render_template("frontpage.html")

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # Basic validation
        if not name or not email or not message:
            flash("Name, email, and message are required fields.", "error")
            return redirect(url_for('contact'))
        data = {'name': name, 'email': email, 'message': message}
        try:
            contact_msg.insert_one(data)
            flash("Data stored successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route('/update_favorite/<room_id>', methods=['POST'])
def update_favorite(room_id):
    room = room.find_one({"_id": ObjectId(room_id)})
    if room:
        new_favorite_status = not room.get('favorite', False)
        room.update_one(
            {"_id": ObjectId(room_id)},
            {"$set": {"favorite": new_favorite_status}}
        )
    return redirect(request.referrer)


@app.route('/toggle_favorite/<room_id>', methods=['POST'])
def toggle_favorite_status(room_id):
    if 'user_id' not in session:
        flash("You need to log in to add favorites.", "info")        
        return redirect(url_for('User_login'))

    room_data = room.find_one({"_id": ObjectId(room_id)})
    
    if room_data:
        new_favorite_status = not room_data.get('favorite', False)
        room.update_one(
            {"_id": ObjectId(room_id)},
            {"$set": {"favorite": new_favorite_status}}
        )
        if new_favorite_status:
            flash("Added to favorites!", "success")
        else:
            flash("Removed from favorites!", "info")
    
    return redirect(request.referrer)

@app.route('/favorite')
def favorite():
    if 'user' in session:
        user = usr.find_one({'username':session['user']})
        if user:
            favorite_rooms = list(room.find({"favorite": True}))
            return render_template('favorite.html', favorite_rooms=favorite_rooms, profile_image=user.get('profile_image', 'img/admin_img.png'),
                                   username=user['username'])

# Route to send request for a room (either to request or cancel a request)
@app.route('/send_request/<room_id>', methods=['POST'])
def send_request(room_id):
    if 'user_id' not in session:
        flash("You need to log in to request a room.", "info")
        return redirect(url_for('User_login'))

    # Retrieve user details from session
    user_id = session.get('user_id', 'N/A')
    username = session.get('user', 'Anonymous')
    email = session.get('email', 'unknown@example.com')

    # Fetch room data
    room_data = room.find_one({"_id": ObjectId(room_id)})
    if room_data:
        requested_by = room_data.get('requested_by', [])
        if not isinstance(requested_by, list):
            requested_by = []

        # Check if user has already requested this room
        user_already_requested = any(req['user_id'] == user_id for req in requested_by)

        if user_already_requested:
            # If user has already requested, cancel the request
            requested_by = [req for req in requested_by if req['user_id'] != user_id]
            new_request_state = False
            flash("Room request canceled.", "success")
        else:
            # Add user's request to the list
            requested_by.append({
                "user_id": user_id,
                "username": username,
                "email": email
            })
            new_request_state = True
            flash("Room request sent successfully!", "success")

        # Update the room with the new requested_by list
        room.update_one(
            {"_id": ObjectId(room_id)},
            {
                "$set": {
                    "request": bool(requested_by),  # True if list is not empty
                    "requested_by": requested_by
                }
            }
        )
    return redirect(request.referrer)


# Route to display requested rooms for the logged-in admin
@app.route('/requested_room')
def requested_room():
    if 'user' in session:
        # Get the current logged-in admin's details
        user = adm.find_one({'username': session['user']})

        if not user:
            return redirect('/login')  # Redirect to login if user is not found

        # Fetch rooms that are requested and owned by the logged-in admin
        requested_rooms = list(room.find({
            "request": True,  # Only rooms with requests
            "username": user['username']  # Only rooms owned by the logged-in admin
        }))

        # Check if the rooms exist and format requested_by correctly
        if requested_rooms:
            for r in requested_rooms:
                r['requested_by'] = r.get('requested_by', [])
                if not isinstance(r['requested_by'], list):
                    r['requested_by'] = []

        return render_template(
            "requested_room.html",
            rooms=requested_rooms,
            username=user['username'],
            profile_image=user.get('profile_image', None)  # Pass profile image if available
        )
    else:
        return redirect('/login')  # Redirect to login if no user in session

if __name__ == "__main__":
    app.run(debug=True)
