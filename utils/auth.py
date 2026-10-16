import bcrypt

def hash_password(password):
    """
    Mengubah teks asli (misal: 'admin123') menjadi hash acak yang aman.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """
    Mengecek apakah password yang diketik cocok dengan hash di Supabase.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))