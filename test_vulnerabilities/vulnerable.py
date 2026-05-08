user = input("Enter username: ")

query = "SELECT * FROM users WHERE name = '" + user + "'"

print(query)
