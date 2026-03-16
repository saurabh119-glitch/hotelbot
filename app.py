# hotel_bot.py - Hotel booking bot
import os
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load room availability (from Google Sheets CSV)
def load_room_data():
    try:
        return pd.read_csv('hotel_rooms.csv', parse_dates=['Date'])
    except:
        # Create sample data if file doesn't exist
        dates = pd.date_range(start=datetime.today(), periods=30)
        data = []
        for date in dates:
            data.append({'Date': date, 'Room_Type': 'Deluxe', 'Available_Rooms': 5, 'Price_Per_Night': 3500})
            data.append({'Date': date, 'Room_Type': 'Suite', 'Available_Rooms': 2, 'Price_Per_Night': 7500})
        df = pd.DataFrame(data)
        df.to_csv('hotel_rooms.csv', index=False)
        return df

def check_availability(check_in, check_out, room_type):
    """Check room availability for given dates"""
    df = load_room_data()
    check_in_dt = pd.to_datetime(check_in)
    check_out_dt = pd.to_datetime(check_out)
    
    date_range = pd.date_range(start=check_in_dt, end=check_out_dt-timedelta(days=1))
    
    for date in date_range:
        available = df[(df['Date'] == date) & (df['Room_Type'] == room_type)]
        if available.empty or available.iloc[0]['Available_Rooms'] <= 0:
            return False, f"No {room_type} rooms available on {date.strftime('%Y-%m-%d')}"
    
    # Calculate total price
    nights = len(date_range)
    price_per_night = df[(df['Date'] == check_in_dt) & (df['Room_Type'] == room_type)].iloc[0]['Price_Per_Night']
    total_price = nights * price_per_night
    
    return True, f"Available! Total: ₹{total_price} for {nights} nights"

def process_booking(guest_name, check_in, check_out, room_type, phone):
    """Process booking and update availability"""
    df = load_room_data()
    check_in_dt = pd.to_datetime(check_in)
    check_out_dt = pd.to_datetime(check_out)
    
    date_range = pd.date_range(start=check_in_dt, end=check_out_dt-timedelta(days=1))
    
    # Update availability
    for date in date_range:
        mask = (df['Date'] == date) & (df['Room_Type'] == room_type)
        df.loc[mask, 'Available_Rooms'] = df.loc[mask, 'Available_Rooms'] - 1
    
    df.to_csv('hotel_rooms.csv', index=False)
    
    # Return booking confirmation
    nights = len(date_range)
    price_per_night = df[(df['Date'] == check_in_dt) & (df['Room_Type'] == room_type)].iloc[0]['Price_Per_Night']
    total_price = nights * price_per_night
    
    return {
        'booking_id': f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'guest_name': guest_name,
        'check_in': check_in,
        'check_out': check_out,
        'room_type': room_type,
        'total_price': total_price,
        'status': 'confirmed'
    }

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """Handle WhatsApp messages"""
    try:
        data = request.get_json()
        message = data.get('message', '').lower()
        phone = data.get('phone', '')
        
        # Simple intent detection
        if 'hello' in message or 'hi' in message:
            response = "Hello! 👋 Welcome to [Hotel Name]! How can I help you?\n\n" \
                      "• Type 'rooms' to see available rooms\n" \
                      "• Type 'book' to make a reservation\n" \
                      "• Type 'amenities' to see facilities"
        
        elif 'rooms' in message:
            today = datetime.today().strftime('%Y-%m-%d')
            tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
            available, msg = check_availability(today, tomorrow, 'Deluxe')
            response = f"🏨 Available Rooms:\n\n" \
                      f"• Deluxe Room: ₹3,500/night\n" \
                      f"• Suite: ₹7,500/night\n\n" \
                      f"Type 'book [room_type] [check_in] [check_out]' to reserve!\n" \
                      f"Example: 'book deluxe 2026-04-15 2026-04-17'"
        
        elif 'book' in message:
            # Parse booking command: "book deluxe 2026-04-15 2026-04-17"
            parts = message.split()
            if len(parts) >= 4:
                room_type = parts[1].title()
                check_in = parts[2]
                check_out = parts[3]
                
                available, msg = check_availability(check_in, check_out, room_type)
                if available:
                    # In real implementation, collect guest name and confirm
                    response = f"✅ Great choice!\n\n" \
                              f"Please confirm your booking:\n" \
                              f"• Room: {room_type}\n" \
                              f"• Check-in: {check_in}\n" \
                              f"• Check-out: {check_out}\n" \
                              f"• Total: {msg}\n\n" \
                              f"Reply 'confirm [your_name]' to complete booking."
                else:
                    response = f"❌ {msg}\n\nTry different dates?"
            else:
                response = "Please use format: 'book [room_type] [check_in] [check_out]'\nExample: 'book deluxe 2026-04-15 2026-04-17'"
        
        elif 'confirm' in message:
            # Parse: "confirm John Doe"
            guest_name = message.replace('confirm', '').strip()
            if guest_name:
                # This would come from previous booking context
                # For demo, use hardcoded values
                booking = process_booking(guest_name, '2026-04-15', '2026-04-17', 'Deluxe', phone)
                response = f"🎉 Booking Confirmed!\n\n" \
                          f"Booking ID: {booking['booking_id']}\n" \
                          f"Guest: {booking['guest_name']}\n" \
                          f"Room: {booking['room_type']}\n" \
                          f"Check-in: {booking['check_in']}\n" \
                          f"Check-out: {booking['check_out']}\n" \
                          f"Total: ₹{booking['total_price']}\n\n" \
                          f"We'll send a confirmation email shortly!"
            else:
                response = "Please provide your full name: 'confirm John Doe'"
        
        elif 'amenities' in message:
            response = "🌟 Hotel Amenities:\n\n" \
                      "• Free WiFi\n" \
                      "• Swimming Pool\n" \
                      "• Restaurant & Bar\n" \
                      "• 24/7 Room Service\n" \
                      "• Free Parking\n" \
                      "• Airport Pickup (₹500)"
        
        else:
            response = "I didn't understand. Try:\n" \
                      "• 'rooms' - See available rooms\n" \
                      "• 'book' - Make a reservation\n" \
                      "• 'amenities' - Hotel facilities"
        
        return jsonify({'response': response})
        
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'response': "Sorry, I'm having trouble. Please call us directly."})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
