from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password

import mysql.connector

import os
import sys

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_mgmt.settings')

import django
django.setup()

from django.contrib.auth.hashers import make_password

def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(username, password, "########## post data ##################")

        try:
            # Connect to MySQL
            conn = mysql.connector.connect(
                host="localhost",
                user="aswin",             # your DB username
                password="Hearzap@123",   # your DB password
                database="hospital_db"
            )
            cursor = conn.cursor(dictionary=True)

            # Fetch user by username and join with role table to get role name
            cursor.execute("""
                SELECT u.*, r.name AS role_name
                FROM users u
                LEFT JOIN role r ON u.role_id = r.id
                WHERE u.username = %s
            """, (username,))
            user = cursor.fetchone()

            print(user, "####### user data ################")

            if user:
                # Check password (assuming you used Django hashing)
                if check_password(password, user['password']):
                    # Set session variables
                    request.session['user_id'] = user['id']
                    request.session['name'] = user['name']
                    request.session['username'] = user['username']
                    request.session['role'] = user['role_name']  # updated here

                    # Redirect to dashboard
                    return redirect('dash_view')
                else:
                    messages.error(request, "Invalid password")
            else:
                messages.error(request, "User not found")

        except mysql.connector.Error as err:
            messages.error(request, f"Database error: {err}")

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    return render(request, 'login_user.html')



def register_user(request):
    roles = []
    specializations = []

    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="aswin",
            password="Hearzap@123",
            database="hospital_db"
        )
        cursor = conn.cursor(dictionary=True)

        # Fetch only Staff and Doctor roles (exclude Patient)
        cursor.execute("SELECT * FROM role WHERE LOWER(name) IN ('doctor', 'staff')")
        roles = cursor.fetchall()

        # Fetch all specializations
        cursor.execute("SELECT * FROM specialization")
        specializations = cursor.fetchall()

    except mysql.connector.Error as err:
        messages.error(request, f"Database error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    # Handle form submission
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        role_name = request.POST.get('role')
        specialization_name = request.POST.get('specialization')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, "register_user.html", {"roles": roles, "specializations": specializations})

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="aswin",
                password="Hearzap@123",
                database="hospital_db"
            )
            cursor = conn.cursor(dictionary=True)

            # Get role_id
            cursor.execute("SELECT id FROM role WHERE name=%s", (role_name,))
            role = cursor.fetchone()
            if not role:
                messages.error(request, "Selected role not found")
                return render(request, "register_user.html", {"roles": roles, "specializations": specializations})

            role_id = role['id']

            # Generate unique username prefix based on role
            prefix = "DOC" if role_name.lower() == "doctor" else "STF"

            # Find latest username with this prefix
            cursor.execute("SELECT username FROM users WHERE username LIKE %s ORDER BY id DESC LIMIT 1", (prefix + '%',))
            last_user = cursor.fetchone()

            if last_user:
                last_num = int(last_user['username'][3:])  # extract number part
                new_num = last_num + 1
            else:
                new_num = 1

            username = f"{prefix}{new_num:03}"  # e.g. DOC001 or STF002

            # Insert new user
            hashed_password = make_password(password)
            cursor.execute("""
                INSERT INTO users (username, name, password, email_id, role_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, name, hashed_password, email, role_id))
            user_id = cursor.lastrowid

            # If doctor, insert into doctor table
            if role_name.lower() == "doctor":
                cursor.execute("SELECT id FROM specialization WHERE name=%s", (specialization_name,))
                spec = cursor.fetchone()
                specialization_id = spec['id'] if spec else None

                cursor.execute("""
                    INSERT INTO doctor (user_id, specialization_id, mobile_number)
                    VALUES (%s, %s, %s)
                """, (user_id, specialization_id, mobile))

            conn.commit()
            messages.success(request, f"{role_name} registered successfully with username {username}!")
            return redirect("auth_register")

        except mysql.connector.Error as err:
            messages.error(request, f"Database error: {err}")

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    return render(request, "register_user.html", {"roles": roles, "specializations": specializations})


def logout_user(request):
    # Clear the user session
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect('auth_login')