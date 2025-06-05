import hashlib
import os

class User:
    def __init__(self, username, password_hash, roles):
        self.username = username
        self.password_hash = password_hash
        self.roles = set(roles) # Store roles as a set for quick lookup

    def verify_password(self, password):
        """Verifies a given password against the stored hash."""
        return hashlib.sha256(password.encode()).hexdigest() == self.password_hash

    def has_role(self, role):
        """Checks if the user has a specific role."""
        return role in self.roles

    def __repr__(self):
        return f"User(username='{self.username}', roles={self.roles})"

class SecurityModule:
    def __init__(self):
        self.users = {}
        self._initialize_default_users()

    def _initialize_default_users(self):
        """Adds some dummy users for demonstration."""
        print("Initializing default users...")
        self.add_user("admin", "adminpass", ["admin", "user"])
        self.add_user("moderator", "modpass", ["moderator", "user"])
        self.add_user("guest", "guestpass", ["user"])
        print("Default users initialized.")

    def hash_password(self, password):
        """Hashes a password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username, password, roles):
        """Adds a new user to the system."""
        if username in self.users:
            print(f"Error: User '{username}' already exists.")
            return False
        password_hash = self.hash_password(password)
        self.users[username] = User(username, password_hash, roles)
        print(f"User '{username}' added with roles: {roles}")
        return True

    def authenticate_user(self, username, password):
        """Authenticates a user based on username and password."""
        user = self.users.get(username)
        if user and user.verify_password(password):
            print(f"Authentication successful for user '{username}'.")
            return user
        else:
            print(f"Authentication failed for user '{username}'. Invalid credentials.")
            return None

    def authorize_action(self, user, required_roles):
        """Checks if a user has any of the required roles for an action."""
        if user is None:
            print("Authorization failed: No user provided.")
            return False
        
        required_roles_set = set(required_roles)
        if not required_roles_set.isdisjoint(user.roles):
            print(f"Authorization successful for user '{user.username}' (required roles: {required_roles_set}, user roles: {user.roles}).")
            return True
        else:
            print(f"Authorization failed for user '{user.username}'. Missing required roles: {required_roles_set - user.roles}.")
            return False

    def list_users(self):
        """Lists all registered users."""
        print("\n--- Registered Users ---")
        if not self.users:
            print("No users registered.")
        for username, user_obj in self.users.items():
            print(f"  - {username}: Roles={user_obj.roles}")
        print("------------------------\n")

if __name__ == "__main__":
    security_mgr = SecurityModule()
    security_mgr.list_users()

    # Test authentication
    print("--- Testing Authentication ---")
    admin_user = security_mgr.authenticate_user("admin", "adminpass")
    invalid_user = security_mgr.authenticate_user("admin", "wrongpass")
    guest_user = security_mgr.authenticate_user("guest", "guestpass")
    non_existent_user = security_mgr.authenticate_user("unknown", "password")

    # Test authorization
    print("\n--- Testing Authorization ---")
    print("\nAdmin actions:")
    security_mgr.authorize_action(admin_user, ["admin"])
    security_mgr.authorize_action(admin_user, ["moderator"]) # Admin is not moderator by default, but has 'user' role
    security_mgr.authorize_action(admin_user, ["user"]) # Admin has 'user' role

    print("\nModerator actions:")
    mod_user = security_mgr.authenticate_user("moderator", "modpass")
    security_mgr.authorize_action(mod_user, ["moderator"])
    security_mgr.authorize_action(mod_user, ["admin"])

    print("\nGuest actions:")
    security_mgr.authorize_action(guest_user, ["user"])
    security_mgr.authorize_action(guest_user, ["admin"])
    security_mgr.authorize_action(guest_user, ["guest_specific_role"]) # This role is not assigned to guest

    print("\nUnauthenticated user actions:")
    security_mgr.authorize_action(invalid_user, ["user"]) # Should fail as invalid_user is None
