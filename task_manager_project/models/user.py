class User:
    """Represents a Standard User in the system."""

    def __init__(
        self,
        username: str,
        password: str,
        is_admin: bool = False,
    ):
        self.username = username
        self.password = password
        self.is_admin = is_admin

    def authenticate(self, password_input: str) -> bool:
        """Validates provided password."""
        return self.password == password_input

    def to_file_format(self) -> str:
        """Serializes user into text format."""
        return f"{self.username}, {self.password}\n"

    def __str__(self) -> str:
        role = "Admin" if self.is_admin else "Standard User"
        return f"User({self.username}, Role: {role})"


class AdminUser(User):
    """Represents an Admin User with full rights."""

    def __init__(self, username: str, password: str):
        super().__init__(username, password, is_admin=True)
