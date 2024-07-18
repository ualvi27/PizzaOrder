import os
import openai
import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

# Set your API key
openai.api_key = st.secrets["openai"]

# Email details
EMAIL_ADDRESS = st.secrets["myemail"]
EMAIL_PASSWORD = st.secrets["mypassword"]
RECIPIENT_EMAIL = os.getenv("Online_Order")

# Menu items with categories, size options, and images
menu = {
    "Pizzas": {
        "Pepperoni Pizza": {
            "Small": 7.00,
            "Medium": 10.00,
            "Large": 12.95,
            "image": "images/peproni1.jpg"
        },
        "Cheese Pizza": {
            "Small": 6.50,
            "Medium": 9.25,
            "Large": 10.95,
            "image": "images/cheeze.jpg"
        },
        "Eggplant Pizza": {
            "Small": 6.75,
            "Medium": 9.75,
            "Large": 11.95,
            "image": "images/eggplant.jpg"
        },
        "Chicken Tikka Pizza": {
            "Small": 6.00,
            "Medium": 8.00,
            "Large": 10.10,
            "image": "images/chktika.jpg"
        }
    },
    "Additional Items": {
        "Fries": {
            "Small": 3.50,
            "Medium": 4.50
        },
        "Greek Salad": {
            "One Size": 7.25
        },
        "Extra Cheese": {
            "One Size": 2.00
        },
        "Mushrooms": {
            "One Size": 1.50
        },
        "Sausage": {
            "One Size": 3.00
        },
        "Canadian Bacon": {
            "One Size": 3.50
        },
        "AI Sauce": {
            "One Size": 1.50
        },
        "Peppers": {
            "One Size": 1.00
        }
    },
    "Drinks": {
        "Coke": {
            "Small": 1.00,
            "Medium": 2.00,
            "Large": 3.00
        },
        "Sprite": {
            "Small": 1.00,
            "Medium": 2.00,
            "Large": 3.00
        },
        "Bottled Water": {
            "One Size": 1.00
        }
    }
}


# Function to send email
def send_email(order_number, order_details, customer_email):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = customer_email
    msg['Subject'] = f"Order Confirmation #{order_number}"

    body = f"""
    The Pizza Shop

    Order Number: {order_number}
    Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    {order_details}

    Thank you for your order! Your order will be ready to pick up in 30 minutes.
    Whatsapp: 03014074704
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, customer_email, text)
        server.quit()
        return "Email sent successfully"
    except Exception as e:
        return f"Failed to send email: {e}"


# Function to save order details to a JSON file
def save_order_to_file(order_number, customer_name, customer_email, order_details):
    order_data = {
        "order_number": order_number,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "order_details": order_details,
        "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(f"order_{order_number}.json", "w") as f:
        json.dump(order_data, f, indent=4)


# Streamlit GUI setup
st.title("Welcome to Pizza Shop")

if "order" not in st.session_state:
    st.session_state.order = {}
    st.session_state.total_price = 0.0
    st.session_state.order_number = 1

# Sidebar with logo and category selection
logo_path = "images/PizzaShop.jpg"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_column_width=True)
st.sidebar.header("Menu")
category = st.sidebar.radio("Select a category", list(menu.keys()))

# Display items in the selected category
st.header(category)
for item, details in menu[category].items():
    if isinstance(details, dict):
        st.subheader(item)
        if "image" in details:
            st.image(details["image"], width=100)
        for size, price in details.items():
            if size == "image":
                continue
            key = f"{item}-{size}"
            if st.checkbox(f"{size} {item} - ${price}", key=key):
                quantity = st.number_input(f"Quantity for {size} {item}", min_value=1, key=f"{key}-quantity")
                st.session_state.order[key] = {"item": item, "size": size, "price": price, "quantity": quantity}

# Display the current order and total price
st.header("Your Order")
if st.session_state.order:
    ordered_items = {}
    total_price = 0.0
    for key, details in st.session_state.order.items():
        item_detail = f"{details['size']} x {details['quantity']}: ${round(details['price'] * details['quantity'], 2)}"
        if details["item"] not in ordered_items:
            ordered_items[details["item"]] = item_detail
        else:
            ordered_items[details["item"]] += f"\n{item_detail}"
        total_price += details['price'] * details['quantity']

    for item, details in ordered_items.items():
        st.write(f"{item}: {details}")

    st.write(f"Total Price: ${round(total_price, 2)}")
    st.session_state.total_price = total_price

# Customer details input
st.header("Customer Details")
customer_name = st.text_input("Name")
customer_email = st.text_input("Email")

if st.button("Confirm Order"):
    order_number = f"PS-{st.session_state.order_number:06d}"
    order_details = "\n".join(f"{item}: {details}" for item, details in ordered_items.items())
    order_details += f"\n\nTotal Price: ${round(st.session_state.total_price, 2)}"

    save_order_to_file(order_number, customer_name, customer_email, order_details)

    email_status = send_email(order_number, order_details, customer_email)
    st.write(f"System: Mail Sent to {customer_email} with order number {order_number}")
    st.write(f"System: {email_status}")
    st.session_state.order_number += 1
    st.session_state.order = {}
    st.session_state.total_price = 0.0
