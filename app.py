import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# Set page config
st.set_page_config(
    page_title="🏨 HotelAI Pro - All-in-One Hotel Assistant",
    page_icon="🏨",
    layout="wide"
)

# Header
st.title("🏨 HotelAI Pro")
st.caption("Your 24/7 AI Hotel Assistant — Reservations, Inquiries, Discounts & More")

# Sidebar: Hotel Info
with st.sidebar:
    st.header("🏨 Welcome to Grand Hotel")
    st.image("https://placehold.co/300x200/3498db/ffffff?text=Grand+Hotel", use_column_width=True)
    st.write("""
    • **Location**: Mumbai, India  
    • **Rating**: ⭐⭐⭐⭐⭐  
    • **Amenities**: Pool, Spa, Restaurant, Free WiFi  
    • **Check-in**: 2 PM | **Check-out**: 12 PM
    """)
    
    st.markdown("---")
    st.subheader("📱 Contact Us")
    st.write("""
    • **Phone**: +91 98765 43210  
    • **Email**: info@grandhotel.com  
    • **WhatsApp**: +91 98765 43210
    """)

# Initialize session state for bookings
if 'booking' not in st.session_state:
    st.session_state.booking = None

# Main Navigation
feature = st.selectbox(
    "How can I help you today?",
    [
        "Select Service",
        "1. Check Room Availability", 
        "2. Get Special Discounts",
        "3. Make a Reservation",
        "4. Ask Questions",
        "5. Share Feedback"
    ]
)

# Feature 1: Room Availability
if feature == "1. Check Room Availability":
    st.header("📅 Check Room Availability")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        check_in = st.date_input("Check-in Date", min_value=datetime.today().date())
    with col2:
        check_out = st.date_input("Check-out Date", min_value=check_in + timedelta(days=1))
    with col3:
        guests = st.number_input("Number of Guests", min_value=1, max_value=4, value=2)
    
    if st.button("Check Availability"):
        if check_out <= check_in:
            st.error("❌ Check-out date must be after check-in date")
        else:
            st.subheader("🏨 Available Rooms")
            
            # Simulate room inventory
            nights = (check_out - check_in).days
            rooms = [
                {"type": "Deluxe Room", "available": 5, "price": 4500, "description": "King bed, city view"},
                {"type": "Premium Suite", "available": 2, "price": 8500, "description": "Separate living area, ocean view"},
                {"type": "Family Room", "available": 3, "price": 6500, "description": "2 bedrooms, kitchenette"}
            ]
            
            for room in rooms:
                if room["available"] > 0:
                    total_price = room["price"] * nights
                    with st.expander(f"{room['type']} - ₹{room['price']}/night ({room['available']} available)"):
                        st.write(f"**Description**: {room['description']}")
                        st.write(f"**Total for {nights} nights**: ₹{total_price:,}")
                        if st.button(f"Select {room['type']}", key=f"select_{room['type']}"):
                            st.session_state.booking = {
                                "room_type": room['type'],
                                "check_in": check_in,
                                "check_out": check_out,
                                "guests": guests,
                                "total_price": total_price
                            }
                            st.success(f"✅ {room['type']} selected! Go to 'Make a Reservation' to complete booking.")

# Feature 2: Discounts
elif feature == "2. Get Special Discounts":
    st.header("💰 Exclusive Discounts & Offers")
    
    st.subheader("🎁 Current Promotions")
    offers = [
        {"name": "Early Bird Special", "discount": "20% off", "conditions": "Book 30+ days in advance"},
        {"name": "Weekend Getaway", "discount": "15% off", "conditions": "Friday-Sunday stays"},
        {"name": "Long Stay Deal", "discount": "25% off", "conditions": "7+ nights"},
        {"name": "Corporate Rate", "discount": "18% off", "conditions": "Business travelers with ID"}
    ]
    
    for offer in offers:
        with st.expander(f"{offer['name']} - {offer['discount']}"):
            st.write(f"**Conditions**: {offer['conditions']}")
            st.write("**How to Avail**: Mention promo code at booking")
    
    st.subheader("🎯 Personalized Discount Calculator")
    col1, col2 = st.columns(2)
    with col1:
        stay_duration = st.slider("Stay Duration (nights)", 1, 14, 3)
        booking_advance = st.slider("Booking in Advance (days)", 1, 60, 15)
    with col2:
        guest_type = st.selectbox("Guest Type", ["Leisure", "Business", "Family", "Couple"])
        room_preference = st.selectbox("Room Type", ["Deluxe", "Premium", "Family"])
    
    if st.button("Calculate Your Discount"):
        base_discount = 10
        if stay_duration >= 7:
            base_discount += 15
        elif stay_duration >= 3:
            base_discount += 5
            
        if booking_advance >= 30:
            base_discount += 10
        elif booking_advance >= 15:
            base_discount += 5
            
        if guest_type == "Business":
            base_discount += 8
        elif guest_type == "Family":
            base_discount += 5
            
        final_discount = min(base_discount, 30)
        st.success(f"🎉 **Your Personalized Discount: {final_discount}% off!**")
        st.info("Use code **HOTELAI2026** at checkout")

# Feature 3: Reservation
elif feature == "3. Make a Reservation":
    st.header("📝 Complete Your Reservation")
    
    if st.session_state.booking is None:
        st.info("Please select a room from 'Check Room Availability' first.")
    else:
        booking = st.session_state.booking
        
        st.subheader("Booking Summary")
        st.write(f"**Room Type**: {booking['room_type']}")
        st.write(f"**Check-in**: {booking['check_in']}")
        st.write(f"**Check-out**: {booking['check_out']}")
        st.write(f"**Guests**: {booking['guests']}")
        st.write(f"**Total Price**: ₹{booking['total_price']:,}")
        
        st.subheader("Guest Details")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name*", key="name")
            email = st.text_input("Email*", key="email")
        with col2:
            phone = st.text_input("Phone Number*", key="phone")
            special_requests = st.text_area("Special Requests", placeholder="Early check-in, extra bed, etc.", key="requests")
        
        promo_code = st.text_input("Promo Code (Optional)", key="promo")
        
        if st.button("Confirm Reservation"):
            if not all([name.strip(), email.strip(), phone.strip()]):
                st.error("❌ Please fill all required fields")
            else:
                discount = 0
                if promo_code.upper() == "HOTELAI2026":
                    discount = 0.2 * booking['total_price']
                    final_price = booking['total_price'] - discount
                else:
                    final_price = booking['total_price']
                
                st.success("✅ Reservation Confirmed!")
                st.subheader("📧 Confirmation Details")
                st.write(f"**Guest**: {name}")
                st.write(f"**Room**: {booking['room_type']}")
                st.write(f"**Dates**: {booking['check_in']} to {booking['check_out']}")
                st.write(f"**Total Paid**: ₹{final_price:,}")
                if discount > 0:
                    st.write(f"**Discount Applied**: ₹{discount:,}")
                st.write(f"**Confirmation Email**: Sent to {email}")
                st.write("**Next Steps**: Check your email for confirmation and check-in instructions.")
                # Clear booking after confirmation
                st.session_state.booking = None

# Feature 4: Inquiries
elif feature == "4. Ask Questions":
    st.header("❓ Hotel Information & FAQs")
    
    faqs = {
        "What are your check-in/check-out times?": "Check-in is at 2 PM and check-out is at 12 PM. Early check-in/late check-out subject to availability.",
        "Do you offer airport pickup?": "Yes! We provide airport pickup for ₹800 one-way. Please book 24 hours in advance.",
        "What amenities do you have?": "We offer swimming pool, spa, restaurant, free WiFi, fitness center, and business center.",
        "Is breakfast included?": "Breakfast is included in Premium Suite bookings. For other rooms, it's available for ₹500 per person.",
        "What is your cancellation policy?": "Free cancellation up to 48 hours before check-in. After that, first night charge applies.",
        "Do you allow pets?": "We're pet-friendly! There's a ₹500 one-time pet fee.",
        "Is parking available?": "Yes, complimentary valet parking for all guests."
    }
    
    question = st.selectbox("Select a Question", list(faqs.keys()))
    st.write(f"**Answer**: {faqs[question]}")
    
    st.markdown("---")
    st.subheader("💬 Ask Your Own Question")
    custom_question = st.text_area("Type your question here...", placeholder="Do you have wheelchair accessible rooms?", key="custom_q")
    if st.button("Get Answer"):
        keywords = {
            "wifi": "Yes, we offer complimentary high-speed WiFi throughout the property.",
            "parking": "Complimentary valet parking is available for all guests.",
            "breakfast": "Breakfast is ₹500 per person, included in Premium Suite bookings.",
            "gym": "Our 24/7 fitness center has modern equipment and personal trainers available.",
            "pool": "Our outdoor pool is open from 6 AM to 8 PM daily."
        }
        
        answer = "I'll connect you with our front desk for personalized assistance!"
        if custom_question:
            comment_lower = custom_question.lower()
            for keyword, response in keywords.items():
                if keyword in comment_lower:
                    answer = response
                    break
        
        st.info(f"**Answer**: {answer}")

# Feature 5: Feedback
elif feature == "5. Share Feedback":
    st.header("⭐ Guest Feedback")
    st.subheader("Help us improve your experience!")
    
    col1, col2 = st.columns(2)
    with col1:
        overall_rating = st.slider("Overall Experience", 1, 5, 4, key="overall")
        cleanliness_rating = st.slider("Cleanliness", 1, 5, 4, key="clean")
        service_rating = st.slider("Staff Service", 1, 5, 4, key="service")
    with col2:
        comfort_rating = st.slider("Room Comfort", 1, 5, 4, key="comfort")
        value_rating = st.slider("Value for Money", 1, 5, 4, key="value")
        wifi_rating = st.slider("WiFi Quality", 1, 5, 4, key="wifi")
    
    comments = st.text_area("Additional Comments", placeholder="What did you love? What can we improve?", key="comments")
    
    if st.button("Submit Feedback"):
        avg_rating = (overall_rating + cleanliness_rating + service_rating + 
                     comfort_rating + value_rating + wifi_rating) / 6
        
        st.success("✅ Thank you for your feedback!")
        st.subheader("📊 Feedback Summary")
        st.write(f"**Average Rating**: {avg_rating:.1f}/5")
        st.write("**Your feedback helps us serve you better!**")

# Footer
st.markdown("---")
st.caption("🏨 HotelAI Pro — Powered by AI | 24/7 Assistance | [Privacy Policy](#) | [Terms of Service](#)")
