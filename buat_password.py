import bcrypt

password_asli = "rahman123"

hashed_password = bcrypt.hashpw(password_asli.encode('utf-8'), bcrypt.gensalt())

print("BERHASIL! Salin teks di bawah ini dan masukkan ke Supabase:")
print("---------------------------------------------------------")
print(hashed_password.decode('utf-8'))
print("---------------------------------------------------------")