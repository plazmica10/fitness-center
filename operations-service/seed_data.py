import requests
import json
from datetime import datetime, timedelta
from uuid import uuid4

BASE_URL = "http://localhost:8080"

def clear_all_data():
    """Clear all data from tables"""
    print("Clearing all data...")
    
    tables = ["attendances", "payments", "classes", "trainers", "rooms"]
    
    # Truncate tables
    for table in tables:
        try:
            response = requests.post(
                "http://localhost:8123",
                auth=("admin", "admin"),
                data=f"TRUNCATE TABLE IF EXISTS {table}"
            )
            if response.status_code == 200:
                print(f"  ✓ Cleared {table}")
            else:
                print(f"  ✗ Failed to clear {table}: {response.text}")
        except Exception as e:
            print(f"  ✗ Error clearing {table}: {e}")

def seed_rooms():
    """Create rooms"""
    print("\nCreating rooms...")
    
    rooms = [
        {"name": "Yoga Studio A", "capacity": 20, "has_equipment": True},
        {"name": "Spin Room", "capacity": 15, "has_equipment": True},
        {"name": "Weight Training Area", "capacity": 30, "has_equipment": True},
        {"name": "Cardio Zone", "capacity": 25, "has_equipment": True},
        {"name": "Group Fitness Room", "capacity": 35, "has_equipment": False},
        {"name": "Pilates Studio", "capacity": 12, "has_equipment": True},
        {"name": "Boxing Ring", "capacity": 10, "has_equipment": True},
        {"name": "Dance Studio", "capacity": 40, "has_equipment": False},
    ]
    
    created_rooms = []
    for room in rooms:
        try:
            response = requests.post(f"{BASE_URL}/rooms/", json=room)
            if response.status_code == 200:
                room_data = response.json()
                created_rooms.append(room_data)
                print(f"  ✓ Created: {room['name']} (ID: {room_data['room_id']})")
            else:
                print(f"  ✗ Failed to create {room['name']}: {response.text}")
        except Exception as e:
            print(f"  ✗ Error creating {room['name']}: {e}")
    
    return created_rooms

def seed_trainers():
    """Create trainers"""
    print("\nCreating trainers...")
    
    trainers = [
        {"name": "Sarah Johnson", "specialization": "yoga", "rating": 4.8},
        {"name": "Mike Chen", "specialization": "strength", "rating": 4.9},
        {"name": "Emma Williams", "specialization": "cardio", "rating": 4.7},
        {"name": "David Martinez", "specialization": "boxing", "rating": 4.6},
        {"name": "Lisa Anderson", "specialization": "pilates", "rating": 4.9},
        {"name": "James Wilson", "specialization": "crossfit", "rating": 4.5},
        {"name": "Rachel Green", "specialization": "dance", "rating": 4.8},
        {"name": "Tom Brown", "specialization": "spinning", "rating": 4.7},
    ]
    
    created_trainers = []
    for trainer in trainers:
        try:
            response = requests.post(f"{BASE_URL}/trainers/", json=trainer)
            if response.status_code == 200:
                trainer_data = response.json()
                created_trainers.append(trainer_data)
                print(f"  ✓ Created: {trainer['name']} - {trainer['specialization']} (ID: {trainer_data['trainer_id']})")
            else:
                print(f"  ✗ Failed to create {trainer['name']}: {response.text}")
        except Exception as e:
            print(f"  ✗ Error creating {trainer['name']}: {e}")
    
    return created_trainers

def seed_classes(trainers, rooms):
    """Create classes"""
    print("\nCreating classes...")
    
    if not trainers or not rooms:
        print("No trainers or rooms available, skipping classes")
        return []
    
    # Create classes for the next 14 days
    start_date = datetime.now()
    created_classes = []
    
    class_templates = [
        {"name": "Morning Yoga", "duration": 60, "capacity": 20, "description": "Start your day with energizing yoga flow"},
        {"name": "HIIT Cardio", "duration": 45, "capacity": 25, "description": "High intensity interval training"},
        {"name": "Strength Training", "duration": 60, "capacity": 15, "description": "Build muscle and strength"},
        {"name": "Spin Class", "duration": 45, "capacity": 15, "description": "Indoor cycling workout"},
        {"name": "Pilates Core", "duration": 50, "capacity": 12, "description": "Core strengthening and flexibility"},
        {"name": "Boxing Basics", "duration": 60, "capacity": 10, "description": "Learn boxing fundamentals"},
        {"name": "Dance Fitness", "duration": 45, "capacity": 30, "description": "Fun dance-based cardio workout"},
        {"name": "Evening Yoga", "duration": 60, "capacity": 20, "description": "Relaxing evening flow"},
    ]
    
    for day in range(14):
        date = start_date + timedelta(days=day)
        
        # Create 3-5 classes per day
        for i in range(3):
            template = class_templates[i % len(class_templates)]
            trainer = trainers[i % len(trainers)]
            room = rooms[i % len(rooms)]
            
            # Morning classes (8am, 10am, 12pm)
            start_hour = 8 + (i * 2)
            start_time = date.replace(hour=start_hour, minute=0, second=0)
            end_time = start_time + timedelta(minutes=template["duration"])
            
            class_data = {
                "name": template["name"],
                "trainer_id": trainer["trainer_id"],
                "room_id": room["room_id"],
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "capacity": template["capacity"],
                "description": template["description"]
            }
            
            try:
                response = requests.post(f"{BASE_URL}/classes/", json=class_data)
                if response.status_code == 200:
                    class_info = response.json()
                    created_classes.append(class_info)
                    print(f"  ✓ Created: {template['name']} on {date.strftime('%Y-%m-%d')} at {start_hour}:00")
                else:
                    print(f"  ✗ Failed to create class: {response.text}")
            except Exception as e:
                print(f"  ✗ Error creating class: {e}")
    
    return created_classes

def seed_members():
    # TODO: integrate with member service in future
    """Generate member IDs"""
    print("\nGenerating member IDs...")
    
    member_ids = [str(uuid4()) for _ in range(50)]
    print(f"  ✓ Generated {len(member_ids)} member IDs")
    return member_ids

def seed_attendances(classes, members):
    """Create attendance records"""
    print("\nCreating attendance records...")
    
    if not classes or not members:
        print("No classes or members available, skipping attendances")
        return []
    
    import random
    created_attendances = []
    statuses = ["checked-in", "checked-out", "cancelled"]
    
    # Create attendances for past classes (last 7 days)
    past_classes = [c for c in classes if datetime.fromisoformat(c["start_time"]) < datetime.now()]
    
    for class_info in past_classes:
        # Random number of attendances (50-90% of capacity)
        capacity = class_info.get("capacity", 20)
        num_attendances = int(capacity * (0.5 + (hash(class_info["class_id"]) % 40) / 100))
        
        # Select UNIQUE random members for this class
        attending_members = random.sample(members, min(num_attendances, len(members)))
        
        for member_id in attending_members:
            # Most are checked-out, some checked-in, few cancelled
            status_weights = [0.1, 0.8, 0.1]  # checked-in, checked-out, cancelled
            status = random.choices(statuses, weights=status_weights)[0]
            
            attendance_data = {
                "class_id": class_info["class_id"],
                "member_id": member_id,
                "timestamp": class_info["start_time"],
                "status": status
            }
            
            try:
                response = requests.post(f"{BASE_URL}/attendances/", json=attendance_data)
                if response.status_code == 200:
                    created_attendances.append(response.json())
            except Exception as e:
                pass  # Silently skip duplicates
        
        print(f"  ✓ Created {len(attending_members)} attendances for {class_info['name']}")
    
    return created_attendances

def seed_payments(classes, members):
    """Create payment records"""
    print("\nCreating payment records...")
    
    if not classes or not members:
        print("No classes or members available, skipping payments")
        return []
    
    import random
    created_payments = []
    
    # Create payments for past classes
    past_classes = [c for c in classes if datetime.fromisoformat(c["start_time"]) < datetime.now()]
    
    for class_info in past_classes:
        capacity = class_info.get("capacity", 20)
        num_payments = int(capacity * (0.5 + (hash(class_info["class_id"]) % 40) / 100))
        
        # Payment amounts based on class type
        base_amounts = {
            "yoga": 15.0,
            "cardio": 12.0,
            "strength": 18.0,
            "spin": 20.0,
            "pilates": 22.0,
            "boxing": 25.0,
            "dance": 10.0,
            "default": 15.0
        }
        
        class_name = class_info['name'].lower()
        amount = next((v for k, v in base_amounts.items() if k in class_name), base_amounts["default"])
        
        # Select UNIQUE random members for payments
        paying_members = random.sample(members, min(num_payments, len(members)))
        
        for member_id in paying_members:
            payment_data = {
                "member_id": member_id,
                "class_id": class_info["class_id"],
                "amount": amount,
                "timestamp": class_info["start_time"]
            }
            
            try:
                response = requests.post(f"{BASE_URL}/payments/", json=payment_data)
                if response.status_code == 200:
                    created_payments.append(response.json())
            except Exception as e:
                pass  # Silently skip duplicates
        
        print(f"  ✓ Created {len(paying_members)} payments for {class_info['name']} (${amount} each)")
    
    return created_payments

def main():
    """Main seeding function"""
    print("=" * 60)
    print("SEEDING")
    print("=" * 60)
    
    # Clear existing data
    clear_all_data()
    
    # Seed data in order (respecting foreign key dependencies)
    rooms = seed_rooms()
    trainers = seed_trainers()
    classes = seed_classes(trainers, rooms)
    members = seed_members()
    attendances = seed_attendances(classes, members)
    payments = seed_payments(classes, members)
    
    # Summary - fetch actual counts from database
    print("\n" + "=" * 60)
    print("SEEDING COMPLETE!")
    print("=" * 60)
    
    try:
        # Get actual counts from API
        rooms_count = len(requests.get(f"{BASE_URL}/rooms/").json())
        trainers_count = len(requests.get(f"{BASE_URL}/trainers/").json())
        classes_count = len(requests.get(f"{BASE_URL}/classes/").json())
        attendances_count = len(requests.get(f"{BASE_URL}/attendances/").json())
        payments_count = len(requests.get(f"{BASE_URL}/payments/").json())
        
        print(f"  Rooms:       {rooms_count}")
        print(f"  Trainers:    {trainers_count}")
        print(f"  Classes:     {classes_count}")
        print(f"  Members:     {len(members)} (generated IDs)")
        print(f"  Attendances: {attendances_count}")
        print(f"  Payments:    {payments_count}")
    except:
        print(f"  Rooms:       {len(rooms)}")
        print(f"  Trainers:    {len(trainers)}")
        print(f"  Classes:     {len(classes)}")
        print(f"  Members:     {len(members)}")
        print(f"  Attendances: {len(attendances)}")
        print(f"  Payments:    {len(payments)}")
    
    print("\nDatabase is ready")
    print("=" * 60)

if __name__ == "__main__":
    main()
