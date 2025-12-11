from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

password = "Admin@123"
hash = bcrypt.generate_password_hash(password).decode()
print("HASH:", hash)
