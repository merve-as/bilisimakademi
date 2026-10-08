import os

class Config:

    # Flask uygulamamızda oturum güvenliği ve form güvenliği için gizli bir anahtar belirliyoruz.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ogrenci-yonetim-gizli-anahtar-2026')

    # -------------------------------------------------------------
    # 1. MS SQL SERVER BAĞLANTI PARAMETRELERİ
    # -------------------------------------------------------------
    # SQL Server sunucu adınız:
    # Eğer varsayılan kurduysanız: 'localhost' veya '.' veya '127.0.0.1'
    # Eğer SQLExpress kurduysanız: r'localhost\SQLEXPRESS' veya r'.\SQLEXPRESS' yazabilirsiniz.
    SQL_SERVER = os.environ.get('SQL_SERVER', '.\\SQLEXPRESS')
    
    # Bağlanmak istediğimiz veritabanı adı (schema.sql ile açtığımız isim):
    SQL_DATABASE = os.environ.get('SQL_DATABASE', 'OgrenciDB')

    # Windows Kimlik Doğrulaması (Windows Authentication) kullanıyorsanız True yapın.
    # Böylece Windows oturumunuzla doğrudan bağlanır, kullanıcı adı/şifre gerekmez.
    SQL_TRUSTED_CONNECTION = True


    # Eğer SQL Server Authentication (sa kullanıcısı gibi) kullanacaksanız:
    # Yukarıdaki SQL_TRUSTED_CONNECTION'ı False yapıp bu bilgileri dolduruyoruz.
    SQL_USER = os.environ.get('SQL_USER', 'sa')
    SQL_PASSWORD = os.environ.get('SQL_PASSWORD', 'Sifreniz123!')


    # Windows'ta yüklü olan SQL Server ODBC sürücüsü. 
    # Genelde 'ODBC Driver 17 for SQL Server' veya 'SQL Server' kullanılır.
    SQL_DRIVER = '{ODBC Driver 17 for SQL Server}'