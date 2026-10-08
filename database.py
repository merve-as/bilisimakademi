# config.py dosyasından içerisinden Config class ını, database.py dosyası içerisine dahil ediyoruz ekliyoruz. database.py dosyası içerisinde kullanabilmek için.
from config import Config
import pyodbc


def get_db_connection():
    """
    Bu fonksiyon veritabanına kapıyı açar (bağlantı nesnesi döner).
    """

     # Bağlantı cümlemizi (Connection String) hazırlıyoruz:
     
    if Config.SQL_TRUSTED_CONNECTION:
        # Windows Authentication (Şifresiz, Windows kullanıcısıyla giriş)
        conn_str = (
            f"DRIVER={Config.SQL_DRIVER};"
            f"SERVER={Config.SQL_SERVER};"
            f"DATABASE={Config.SQL_DATABASE};"
            f"Trusted_Connection=yes;"
        )
    else:
        # SQL Server Authentication (Kullanıcı adı ve şifre ile giriş)
        conn_str = (
            f"DRIVER={Config.SQL_DRIVER};"
            f"SERVER={Config.SQL_SERVER};"
            f"DATABASE={Config.SQL_DATABASE};"
            f"UID={Config.SQL_USER};"
            f"PWD={Config.SQL_PASSWORD};"
        )
    
    # Bağlantıyı açıyoruz ve timeout süresini kısa tutuyoruz ki bekletmesin
    conn = pyodbc.connect(conn_str, timeout=3)
    return conn



# ===================================================================
# ÖĞRENCİ CRUD (Create, Read, Update, Delete) FONKSİYONLARI
# ===================================================================

def get_all_students(search_query=None):
    """
    Tüm öğrencileri ve aldıkları kursun adını (JOIN kullanarak) getirir.
    """
    conn = get_db_connection()

    # cursor: SQL Server a bağlanıp sql sorgusunu çalıştırıp geriye sonucu bize döner.
    cursor = conn.cursor()
    
    # SQL sorgumuz: Öğrenci bilgilerini Kurslar tablosu ile birleştiriyoruz
    sql = """
        SELECT 
            o.OgrenciID, o.Ad, o.Soyad, o.Email, o.Telefon, o.NotOrtalamasi, o.KursID,
            k.KursAdi, k.Kategori
        FROM Ogrenciler o LEFT JOIN Kurslar k ON o.KursID = k.KursID
    """
    params = []
    
    # Eğer arama kutusuna bir şey yazıldıysa WHERE filtresi ekliyoruz:
    if search_query:
        sql += " WHERE o.Ad LIKE ? OR o.Soyad LIKE ? OR o.Email LIKE ?"
        arama = f"%{search_query}%"
        params = [arama, arama, arama]
        
    sql += " ORDER BY o.OgrenciID DESC"
    
    # Sorguyu çalıştırıyoruz:
    cursor.execute(sql, params)
    
    # Gelen satırları temiz bir Python listesi (sözlükler) haline çeviriyoruz:
    students = []

    # cursor.fetchall(): sql sorgusundan dönen bütün sonuçları alıyoruz ve rows ismindeki değişken içerisinde atıyoruz.
    rows = cursor.fetchall()
    
    for row in rows:
        students.append({
            "OgrenciID": row[0],
            "Ad": row[1],
            "Soyad": row[2],
            "Email": row[3],
            "Telefon": row[4] or "-",
            "NotOrtalamasi": float(row[5]) if row[5] is not None else 0.0,
            "KursID": row[6],
            "KursAdi": row[7] if row[7] else "Kurs Atanmadı",
            "Kategori": row[8] if row[8] else "Genel"
        })
        
    conn.close() # İşimiz bitince bağlantıyı kapatıyoruz (Kaynak tasarrufu)
    return students

def get_student_by_id(student_id):
    """
    ID numarası verilen tek bir öğrencinin detayını getirir (Öğrencinin Düzenleme formu için).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT OgrenciID, Ad, Soyad, Email, Telefon, NotOrtalamasi, KursID FROM Ogrenciler WHERE OgrenciID = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "OgrenciID": row[0],
            "Ad": row[1],
            "Soyad": row[2],
            "Email": row[3],
            "Telefon": row[4],
            "NotOrtalamasi": float(row[5]) if row[5] is not None else 0.0,
            "KursID": row[6]
        }
    return None

def add_student(ad, soyad, email, telefon, not_ortalamasi, kurs_id):
    """
    Yeni öğrenci ekleme fonksiyonu (INSERT INTO).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = """
        INSERT INTO Ogrenciler (Ad, Soyad, Email, Telefon, NotOrtalamasi, KursID)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(sql, (ad, soyad, email, telefon, not_ortalamasi, kurs_id or None))
    conn.commit()  # Değişiklikleri kalıcı olarak veritabanına işliyoruz!
    conn.close()
    return True

def update_student(student_id, ad, soyad, email, telefon, not_ortalamasi, kurs_id):
    """
    Var olan bir öğrencinin bilgilerini günceller (UPDATE).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = """
        UPDATE Ogrenciler 
        SET Ad = ?, Soyad = ?, Email = ?, Telefon = ?, NotOrtalamasi = ?, KursID = ?
        WHERE OgrenciID = ?
    """
    cursor.execute(sql, (ad, soyad, email, telefon, not_ortalamasi, kurs_id or None, student_id))
    conn.commit()
    conn.close()
    return True

def delete_student(student_id):
    """
    Öğrenci silme fonksiyonu (DELETE FROM).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM Ogrenciler WHERE OgrenciID = ?", (student_id,))
    conn.commit()
    conn.close()
    return True



# ===================================================================
# KURS VE İSTATİSTİK FONKSİYONLARI (DASHBOARD İÇİN)
# ===================================================================


def get_all_courses():
    """
    Sistemdeki tüm kursları listeler.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT KursID, KursAdi, Egitmen, Kredi, Kategori FROM Kurslar ORDER BY KursAdi ASC")
    rows = cursor.fetchall()
    
    courses = []
    for row in rows:
        courses.append({
            "KursID": row[0],
            "KursAdi": row[1],
            "Egitmen": row[2],
            "Kredi": row[3],
            "Kategori": row[4]
        })
    conn.close()
    return courses




def add_course(kurs_adi, egitmen, kredi, kategori):
    """
    Yeni bir kurs oluşturur.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO Kurslar (KursAdi, Egitmen, Kredi, Kategori)
        VALUES (?, ?, ?, ?)
    """, (kurs_adi, egitmen, kredi, kategori))
    conn.commit()
    conn.close()
    return True


def get_dashboard_stats():
    """
    Yönetim panelindeki renkli özet kartlar ve grafikler için 
    sayımları ve ortalamaları hesaplayan SQL sorgularını çalıştırır.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Toplam Öğrenci Sayısı
    cursor.execute("SELECT COUNT(*) FROM Ogrenciler")
    total_students = cursor.fetchone()[0]
    
    # 2. Toplam Kurs Sayısı
    cursor.execute("SELECT COUNT(*) FROM Kurslar")
    total_courses = cursor.fetchone()[0]
    
    # 3. Genel Not Ortalaması
    cursor.execute("SELECT AVG(NotOrtalamasi) FROM Ogrenciler")
    avg_grade = cursor.fetchone()[0]
    avg_grade = round(float(avg_grade), 2) if avg_grade is not None else 0.0
    
    # 4. Başarılı Öğrenci Sayısı (Notu 70 ve üzeri olanlar)
    cursor.execute("SELECT COUNT(*) FROM Ogrenciler WHERE NotOrtalamasi >= 70")
    successful_students = cursor.fetchone()[0]
    
    # 5. Kurs Başına Öğrenci Sayısı (Grafik İçin - GROUP BY Sorgusu)
    cursor.execute("""
        SELECT k.KursAdi, COUNT(o.OgrenciID) AS OgrenciSayisi
        FROM Kurslar k LEFT JOIN Ogrenciler o ON k.KursID = o.KursID
        GROUP BY k.KursID, k.KursAdi
    """)
    course_distribution = [{"kurs": row[0], "sayi": row[1]} for row in cursor.fetchall()]

    # Yazılım 17
    # Veritabanı 13
    # Web Tasarım 3


    conn.close()
    
    return {
        "total_students": total_students,
        "total_courses": total_courses,
        "avg_grade": avg_grade,
        "successful_students": successful_students,
        "course_distribution": course_distribution
    }



# ===================================================================
# GİRİŞ VE OTURUM (AUTH) FONKSİYONLARI
# ===================================================================

def check_user_login(kullanici_adi, sifre):
    """
    Veritabanından kullanıcının girdiği 'Kullanıcı Adı' ve 'Şifre'yi sorgular.
    """

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # SQL sorgumuz:
    sql = "SELECT KullaniciID, KullaniciAdi, AdSoyad, Rol FROM Kullanicilar WHERE KullaniciAdi = ? AND Sifre = ?"
    
    cursor.execute(sql, (kullanici_adi, sifre))
    row = cursor.fetchone()
    
    conn.close()
    
    # Eğer eşleşen bir kayıt (satır) varsa bu bilgileri döndür, yoksa None (boş) döndür
    if row:
        return {
            "KullaniciID": row[0],
            "KullaniciAdi": row[1],
            "AdSoyad": row[2],
            "Rol": row[3]
        }
    return None