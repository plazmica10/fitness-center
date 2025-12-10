"""
User Service Sync Module
Handles synchronization of trainer data with the user service
"""
import httpx
import os

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8000")
ADMIN_USERNAME = os.getenv("USER_SERVICE_ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("USER_SERVICE_ADMIN_PASSWORD")


async def create_user_for_trainer(trainer_id: str, name: str, email: str = None, password: str = None):
    """
    Create a user account in the user service for a trainer
    """
    if not email:
        name_lowercase = name.lower().replace(" ", "")
        email = f"{name_lowercase}@fitness.com"
    
    name_lowercase = name.lower().replace(" ", "")
    username = name_lowercase
    if not password:
        password = "123456"  # Default password
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{USER_SERVICE_URL}/register",
                json={
                    "username": username,
                    "email": email,
                    "full_name": name,
                    "password": password,
                    "role": "trainer"
                },
                timeout=5.0
            )
            
            if response.status_code == 201:
                print(f"[SUCCESS] Created user account for trainer: {username}")
                return response.json()
            elif response.status_code == 400 and "already exists" in response.text:
                print(f"[INFO] User {username} already exists")
                return None
            else:
                print(f"[ERROR] Failed to create user for trainer {name}: {response.text}")
                return None
                
        except Exception as e:
            print(f"[ERROR] Error creating user for trainer {name}: {e}")
            return None


async def _get_admin_token() -> str | None:
    """Login as admin to the user service and return a bearer token"""
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        print("[WARN] Missing USER_SERVICE_ADMIN_USERNAME/PASSWORD envs; cannot delete trainer user")
        return None

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{USER_SERVICE_URL}/login",
                json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
                timeout=5.0
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("access_token")
            print(f"[ERROR] Admin login failed: {resp.status_code} {resp.text}")
            return None
        except Exception as e:
            print(f"[ERROR] Admin login error: {e}")
            return None


async def _find_user_id_by_username(token: str, username: str) -> str | None:
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        try:
            # Filter to role=trainer to reduce payload
            resp = await client.get(f"{USER_SERVICE_URL}/users", params={"role": "trainer"}, headers=headers, timeout=7.0)
            if resp.status_code != 200:
                print(f"[ERROR] List users failed: {resp.status_code} {resp.text}")
                return None
            users = resp.json() or []
            for u in users:
                if u.get("username") == username:
                    return u.get("_id") or u.get("id")
            return None
        except Exception as e:
            print(f"[ERROR] Error listing users: {e}")
            return None


async def _delete_user_by_id(token: str, user_id: str) -> bool:
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.delete(f"{USER_SERVICE_URL}/users/{user_id}", headers=headers, timeout=5.0)
            if resp.status_code in (204, 200):
                return True
            print(f"[ERROR] Delete user failed: {resp.status_code} {resp.text}")
            return False
        except Exception as e:
            print(f"[ERROR] Error deleting user: {e}")
            return False


async def delete_user_for_trainer(trainer_id: str, name: str = None, bearer_token: str | None = None):
    """
    Delete a user account in the user service for a trainer
    Requires admin authentication via USER_SERVICE_ADMIN_USERNAME/PASSWORD envs
    """
    if not name:
        print(f"[INFO] No trainer name provided; cannot derive username for trainer_id={trainer_id}")
        return None

    username = name.lower().replace(" ", "")
    token = bearer_token or await _get_admin_token()
    if not token:
        print(f"[WARN] Skipping deletion for trainer user '{username}' due to missing admin token")
        return None

    user_id = await _find_user_id_by_username(token, username)
    if not user_id:
        print(f"[INFO] Trainer user '{username}' not found in user service; nothing to delete")
        return None

    ok = await _delete_user_by_id(token, user_id)
    if ok:
        print(f"[SUCCESS] Deleted user '{username}' (id={user_id}) for trainer {trainer_id}")
    return None
