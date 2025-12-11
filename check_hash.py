from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

hash = "$2b$12$Q/Co.LcUuA3TBUnIFJnyUuVZlbtJfxxG5PXzzpzrTNHfAuT7nRdxO"
print(bcrypt.check_password_hash(hash, "Admin@123"))
