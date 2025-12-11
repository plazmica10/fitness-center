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
            response = requests.post(f"{BASE_URL}/rooms/", json=room, timeout=10)
            if response.status_code == 200:
                room_data = response.json()
                created_rooms.append(room_data)
                print(f"  ✓ Created: {room['name']} (ID: {room_data.get('room_id', 'N/A')})")
            else:
                print(f"  ✗ Failed to create {room['name']}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"  ✗ Error creating {room['name']}: {e}")
    
    return created_rooms

def get_admin_token():
    """Get admin token for authenticated requests"""
    try:
        response = requests.post(
            "http://localhost:8000/login",
            json={"username": "admin", "password": "123456"},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()["access_token"]
    except:
        pass
    return None


def seed_trainers(admin_token=None):
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
    
    headers = {}
    if admin_token:
        headers["Authorization"] = f"Bearer {admin_token}"
    
    created_trainers = []
    for trainer in trainers:
        try:
            response = requests.post(f"{BASE_URL}/trainers/", json=trainer, headers=headers)
            if response.status_code == 200:
                trainer_data = response.json()
                created_trainers.append(trainer_data)
                print(f"  ✓ Created: {trainer['name']} - {trainer['specialization']} (ID: {trainer_data['trainer_id']})")
            else:
                print(f"  ✗ Failed to create {trainer['name']}: {response.text}")
        except Exception as e:
            print(f"  ✗ Error creating {trainer['name']}: {e}")
    
    return created_trainers

def seed_classes(trainers, rooms, admin_token=None):
    """Create classes"""
    print("\nCreating classes...")
    
    if not trainers or not rooms:
        print("No trainers or rooms available, skipping classes")
        return []
    
    headers = {}
    if admin_token:
        headers["Authorization"] = f"Bearer {admin_token}"
    
    # Create classes starting from tomorrow for the next 14 days
    start_date = datetime.now() + timedelta(days=1)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    created_classes = []
    
    class_templates = [
        {"name": "Morning Yoga", "duration": 60, "capacity": 20, "price": 15.0, "description": "Start your day with energizing yoga flow"},
        {"name": "HIIT Cardio", "duration": 45, "capacity": 25, "price": 12.0, "description": "High intensity interval training"},
        {"name": "Strength Training", "duration": 60, "capacity": 15, "price": 18.0, "description": "Build muscle and strength"},
        {"name": "Spin Class", "duration": 45, "capacity": 15, "price": 20.0, "description": "Indoor cycling workout"},
        {"name": "Pilates Core", "duration": 50, "capacity": 12, "price": 22.0, "description": "Core strengthening and flexibility"},
        {"name": "Boxing Basics", "duration": 60, "capacity": 10, "price": 25.0, "description": "Learn boxing fundamentals"},
        {"name": "Dance Fitness", "duration": 45, "capacity": 30, "price": 10.0, "description": "Fun dance-based cardio workout"},
        {"name": "Evening Yoga", "duration": 60, "capacity": 20, "price": 15.0, "description": "Relaxing evening flow"},
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
                "price": template["price"],
                "description": template["description"]
            }
            
            try:
                response = requests.post(f"{BASE_URL}/classes/", json=class_data, headers=headers, timeout=10)
                if response.status_code == 200:
                    class_info = response.json()
                    created_classes.append(class_info)
                    print(f"  ✓ Created: {template['name']} on {date.strftime('%Y-%m-%d')} at {start_hour}:00")
                else:
                    print(f"  ✗ Failed to create class: {response.text[:100]}")
            except Exception as e:
                print(f"  ✗ Error creating class: {e}")
    
    return created_classes

def seed_members(admin_token=None):
    """Fetch actual member IDs from MongoDB user service"""
    from uuid import uuid4
    print("\nFetching member IDs from user service...")
    
    try:
        headers = {}
        if admin_token:
            headers["Authorization"] = f"Bearer {admin_token}"
        
        # Fetch all users from user service
        response = requests.get(
            "http://localhost:8000/users",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            users = response.json()
            # Filter members and create username -> MongoDB ID mapping
            member_map = {}
            for user in users:
                if user.get("role") == "member":
                    username = user.get("username")
                    user_id = user.get("id") or user.get("_id")
                    if username and user_id:
                        member_map[username] = user_id
            
            print(f"  ✓ Fetched {len(member_map)} member IDs from MongoDB")
            return member_map
        else:
            print(f"  ✗ Failed to fetch users: HTTP {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error fetching users: {e}")
    
    # Fallback: Generate UUIDs if user service is unavailable
    print("  ⚠ Using fallback UUIDs (member names won't match)")
    member_usernames = [
        "alex_chen", "bella_rodriguez", "carlos_garcia", "diana_patel",
        "ethan_kim", "fiona_murphy", "gabriel_santos", "hannah_cohen",
        "isaac_wright", "julia_lopez", "kevin_nguyen", "laura_brown",
        "marcus_davis", "nina_anderson", "oliver_wilson", "petra_silva",
        "quinn_taylor", "rachel_moore", "sofia_martin", "tyler_jackson",
        "uma_patel", "victor_lee", "wendy_white", "xavier_jones",
        "yuki_tanaka", "zara_ali", "aaron_hill", "bridget_scott",
        "chloe_green", "daniel_baker"
    ]
    member_map = {username: str(uuid4()) for username in member_usernames}
    return member_map

def seed_attendances(classes, member_map):
    """Create attendance records"""
    print("\nCreating attendance records...")
    
    if not classes or not member_map:
        print("No classes or members available, skipping attendances")
        return []
    
    import random
    created_attendances = []
    
    # Create attendances for upcoming classes (simulate pre-bookings)
    # Take first 20 classes to create bookings
    member_ids = list(member_map.values())
    
    for class_info in classes[:20]:
        # Random number of attendances (50-90% of capacity)
        capacity = class_info.get("capacity", 20)
        if capacity is None:
            capacity = 20
        num_attendances = int(capacity * (0.5 + (hash(str(class_info["class_id"])) % 40) / 100))
        
        # Select UNIQUE random member IDs for this class
        attending_member_ids = random.sample(member_ids, min(num_attendances, len(member_ids)))
        
        for member_id in attending_member_ids:
            attendance_data = {
                "class_id": class_info["class_id"],
                "member_id": member_id,
                "timestamp": class_info["start_time"],
                "status": "checked-in"
            }
            
            try:
                response = requests.post(f"{BASE_URL}/attendances/", json=attendance_data, timeout=10)
                if response.status_code == 200:
                    created_attendances.append(response.json())
                else:
                    print(f"  ✗ Failed to create attendance: HTTP {response.status_code} - {response.text[:100]}")
            except Exception as e:
                print(f"  ✗ Error creating attendance: {e}")
        
        print(f"  ✓ Attempted {len(attending_member_ids)} attendances for {class_info['name']}")
    
    return created_attendances

def seed_payments(classes, member_map, attendances, admin_token=None):
    """Create payment records for members with attendances"""
    print("\nCreating payment records...")
    
    if not classes or not member_map or not attendances:
        print("No classes, members, or attendances available, skipping payments")
        return []
    
    created_payments = []
    headers = {}
    if admin_token:
        headers["Authorization"] = f"Bearer {admin_token}"
    
    # Create payment for each attendance
    # Group attendances by class_id to get members who booked
    from collections import defaultdict
    attendance_by_class = defaultdict(list)
    for att in attendances:
        attendance_by_class[att["class_id"]].append(att["member_id"])
    
    for class_id, member_ids in attendance_by_class.items():
        # Find the class info
        class_info = next((c for c in classes if c["class_id"] == class_id), None)
        if not class_info:
            continue
        
        # Use the price from the class, or default to 15.0
        amount = class_info.get('price', 15.0)
        if amount is None:
            amount = 15.0
        
        # Create payment for each member who has attendance
        for member_id in member_ids:
            payment_data = {
                "member_id": member_id,
                "class_id": class_info["class_id"],
                "amount": float(amount),
                "timestamp": class_info["start_time"],
                "status": "completed"
            }
            
            try:
                response = requests.post(f"{BASE_URL}/payments/", json=payment_data, headers=headers, timeout=10)
                if response.status_code == 200:
                    created_payments.append(response.json())
            except Exception as e:
                pass  # Silently skip errors
        
        print(f"  ✓ Created {len(member_ids)} payments for {class_info['name']} (${amount} each)")
    
    return created_payments

def wait_for_services():
    """Wait for services to be ready"""
    print("\nWaiting for services to be ready...")
    
    import time
    max_retries = 30
    for i in range(max_retries):
        try:
            user_resp = requests.get("http://localhost:8000/", timeout=2)
            ops_resp = requests.get(f"{BASE_URL}/", timeout=2)
            
            if user_resp.status_code == 200 and ops_resp.status_code == 200:
                print("  ✓ All services are ready!")
                return True
        except requests.RequestException:
            pass
        
        print(f"  Waiting... ({i+1}/{max_retries})")
        time.sleep(2)
    
    print("  ✗ Services did not become ready in time")
    return False


def drop_mongodb_collections():
    """Drop all collections in MongoDB to start fresh"""
    print("\n  Deleting all users via API...")
    
    # First try to get admin token
    admin_token = None
    try:
        response = requests.post(
            "http://localhost:8000/login",
            json={"username": "admin", "password": "123456"},
            timeout=5
        )
        if response.status_code == 200:
            admin_token = response.json()["access_token"]
    except:
        pass
    
    if not admin_token:
        print("  ⚠ Could not get admin token, cannot delete users via API")
        print("  ⚠ Trying direct MongoDB connection...")
        try:
            from pymongo import MongoClient
            client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
            db = client["fitness_users"]
            
            # Drop the users collection
            if "users" in db.list_collection_names():
                db.users.drop()
                print("  ✓ Dropped 'users' collection from MongoDB")
            else:
                print("  ℹ No 'users' collection found, starting fresh")
            
            client.close()
            return True
        except Exception as e:
            print(f"  ⚠ Could not drop collections: {e}")
            return True  # Continue anyway
    
    # Get all users
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get("http://localhost:8000/users", headers=headers, timeout=5)
        
        if response.status_code != 200:
            print(f"  ⚠ Could not fetch users: {response.status_code}")
            return True
        
        users = response.json()
        deleted_count = 0
        
        for user in users:
            user_id = user.get("id") or user.get("_id")
            if user_id:
                try:
                    del_resp = requests.delete(
                        f"http://localhost:8000/users/{user_id}",
                        headers=headers,
                        timeout=5
                    )
                    if del_resp.status_code in [204, 200]:
                        deleted_count += 1
                except:
                    pass
        
        print(f"  ✓ Deleted {deleted_count} users from MongoDB")
        return True
        
    except Exception as e:
        print(f"  ⚠ Error deleting users: {e}")
        return True  # Continue anyway


def create_user(username, email, full_name, password, role, balance=150.0):
    """Create a user in the user service with initial balance"""
    try:
        response = requests.post(
            "http://localhost:8000/register",
            json={
                "username": username,
                "email": email,
                "full_name": full_name,
                "password": password,
                "role": role,
                "balance": balance
            },
            timeout=5
        )
        
        if response.status_code == 201:
            print(f"  ✓ Created {role}: {username}")
            return response.json()
        elif response.status_code == 400 and "already exists" in response.text:
            print(f"  ⚠ User {username} already exists, skipping")
            return None
        else:
            print(f"  ✗ Failed to create user {username}")
            return None
            
    except requests.RequestException as e:
        print(f"  ✗ Error creating user {username}: {e}")
        return None


def seed_mongodb_users():
    """Create all MongoDB users: admin, trainers, and members"""
    import time
    print("\n" + "=" * 60)
    print("CREATING MONGODB USERS")
    print("=" * 60)
    
    # Create admin
    print("\nCreating admin user...")
    create_user("admin", "admin@fitness.com", "Admin User", "123456", "admin")
    time.sleep(0.3)
    
    # Create test trainer
    print("\nCreating test trainer...")
    create_user("john_trainer", "john@fitness.com", "John Smith", "123456", "trainer")
    time.sleep(0.3)
    
    # Create member users
    print("\nCreating member users...")
    members = [
        {"username": "alex_chen", "full_name": "Alex Chen"},
        {"username": "bella_rodriguez", "full_name": "Bella Rodriguez"},
        {"username": "carlos_garcia", "full_name": "Carlos Garcia"},
        {"username": "diana_patel", "full_name": "Diana Patel"},
        {"username": "ethan_kim", "full_name": "Ethan Kim"},
        {"username": "fiona_murphy", "full_name": "Fiona Murphy"},
        {"username": "gabriel_santos", "full_name": "Gabriel Santos"},
        {"username": "hannah_cohen", "full_name": "Hannah Cohen"},
        {"username": "isaac_wright", "full_name": "Isaac Wright"},
        {"username": "julia_lopez", "full_name": "Julia Lopez"},
        {"username": "kevin_nguyen", "full_name": "Kevin Nguyen"},
        {"username": "laura_brown", "full_name": "Laura Brown"},
        {"username": "marcus_davis", "full_name": "Marcus Davis"},
        {"username": "nina_anderson", "full_name": "Nina Anderson"},
        {"username": "oliver_wilson", "full_name": "Oliver Wilson"},
        {"username": "petra_silva", "full_name": "Petra Silva"},
        {"username": "quinn_taylor", "full_name": "Quinn Taylor"},
        {"username": "rachel_moore", "full_name": "Rachel Moore"},
        {"username": "sofia_martin", "full_name": "Sofia Martin"},
        {"username": "tyler_jackson", "full_name": "Tyler Jackson"},
        {"username": "uma_patel", "full_name": "Uma Patel"},
        {"username": "victor_lee", "full_name": "Victor Lee"},
        {"username": "wendy_white", "full_name": "Wendy White"},
        {"username": "xavier_jones", "full_name": "Xavier Jones"},
        {"username": "yuki_tanaka", "full_name": "Yuki Tanaka"},
        {"username": "zara_ali", "full_name": "Zara Ali"},
        {"username": "aaron_hill", "full_name": "Aaron Hill"},
        {"username": "bridget_scott", "full_name": "Bridget Scott"},
        {"username": "chloe_green", "full_name": "Chloe Green"},
        {"username": "daniel_baker", "full_name": "Daniel Baker"},
    ]
    
    created_count = 0
    for member in members:
        username = member["username"]
        result = create_user(
            username=username,
            email=f"{username}@fitness.com",
            full_name=member["full_name"],
            password="123456",
            role="member"
        )
        if result:
            created_count += 1
        time.sleep(0.2)
    
    print(f"\n  ✓ Created {created_count} member users")


def sync_trainers_to_mongodb():
    """Sync trainers from ClickHouse to MongoDB"""
    import time
    print("\n" + "=" * 60)
    print("SYNCING TRAINERS TO MONGODB")
    print("=" * 60)
    
    # Get trainers from operations service
    try:
        response = requests.get(f"{BASE_URL}/trainers/", timeout=10)
        if response.status_code != 200:
            print("  ✗ Failed to fetch trainers")
            return
        
        trainers = response.json()
        print(f"\n  Found {len(trainers)} trainers in ClickHouse")
        
        success_count = 0
        for trainer in trainers:
            trainer_id = str(trainer.get("trainer_id", ""))
            name = trainer.get("name", "")
            
            if not trainer_id or not name:
                continue
            
            # Use lowercase name without spaces for username and email
            name_lowercase = name.lower().replace(" ", "")
            username = name_lowercase
            email = f"{name_lowercase}@fitness.com"
            
            result = create_user(
                username=username,
                email=email,
                full_name=name,
                password="123456",
                role="trainer"
            )
            if result:
                success_count += 1
            time.sleep(0.3)
        
        print(f"\n  ✓ Synced {success_count} trainers to MongoDB")
        
    except Exception as e:
        print(f"  ✗ Error syncing trainers: {e}")


def main():
    """Main seeding function"""
    print("\n" + "=" * 60)
    print("FITNESS CENTER - COMPLETE DATABASE SETUP")
    print("=" * 60)
    
    # Wait for services
    if not wait_for_services():
        print("\n✗ Services are not ready. Please start docker-compose first.")
        return
    
    # Drop MongoDB collections
    print("\n" + "=" * 60)
    print("CLEARING MONGODB")
    print("=" * 60)
    drop_mongodb_collections()
    
    # Seed MongoDB users (admin, members, and test trainer)
    seed_mongodb_users()
    
    # Clear ClickHouse data
    print("\n" + "=" * 60)
    print("CLEARING CLICKHOUSE DATA")
    print("=" * 60)
    clear_all_data()
    
    # Get admin token for authenticated requests
    print("\n" + "=" * 60)
    print("GETTING ADMIN TOKEN")
    print("=" * 60)
    admin_token = get_admin_token()
    if admin_token:
        print("  ✓ Logged in as admin")
    else:
        print("  ✗ Failed to get admin token - some operations may fail")
    
    # Seed ClickHouse data in order (respecting foreign key dependencies)
    print("\n" + "=" * 60)
    print("SEEDING CLICKHOUSE DATA")
    print("=" * 60)
    rooms = seed_rooms()
    trainers = seed_trainers(admin_token)
    classes = seed_classes(trainers, rooms, admin_token)
    member_map = seed_members(admin_token)
    attendances = seed_attendances(classes, member_map)
    payments = seed_payments(classes, member_map, attendances, admin_token)
    
    # Sync trainers from ClickHouse to MongoDB
    sync_trainers_to_mongodb()
    
    # Summary
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    
    try:
        # Get actual counts from API
        rooms_count = len(requests.get(f"{BASE_URL}/rooms/").json())
        trainers_count = len(requests.get(f"{BASE_URL}/trainers/").json())
        classes_count = len(requests.get(f"{BASE_URL}/classes/").json())
        attendances_count = len(requests.get(f"{BASE_URL}/attendances/").json())
        payments_count = len(requests.get(f"{BASE_URL}/payments/").json())
        
        print("\nClickHouse Database:")
        print(f"  Rooms:       {rooms_count}")
        print(f"  Trainers:    {trainers_count}")
        print(f"  Classes:     {classes_count}")
        print(f"  Attendances: {attendances_count}")
        print(f"  Payments:    {payments_count}")
    except:
        print("\nClickHouse Database:")
        print(f"  Rooms:       {len(rooms)}")
        print(f"  Trainers:    {len(trainers)}")
        print(f"  Classes:     {len(classes)}")
        print(f"  Attendances: {len(attendances)}")
        print(f"  Payments:    {len(payments)}")
    
    print("\nMongoDB Database:")
    print(f"  Admin:       1")
    print(f"  Trainers:    ~9 (1 test + 8 synced)")
    print(f"  Members:     30")
    
    print("\nLogin Credentials (all passwords: 123456):")
    print("  Admin:       admin / 123456")
    print("  Trainer:     jameswilson / 123456 (or other trainer names)")
    print("  Member:      alex_chen / 123456 (or other member usernames)")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Script interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
