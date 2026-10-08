# Uygulamamızın Beynidir. Bütün yönetimi burası yapar, gelen isteklerin hepsi önce buraya düşer.

# Web uygulamamızın beyni burasıdır! Kullanıcı bir sayfaya 
# tıkladığında veya butonla form gönderdiğinde istek (Request) buraya gelir. 
# Biz de Python ile veritabanına gider, veriyi alır ve HTML sayfasına yollarız.

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from config import Config

from functools import wraps # Güvenlik önlemi için login methodunu sarmalayan adını değiştiren bir güvenlik yapısıdır.

import database as db

# session: Uygulamanın çalıştırıldığı bilgisayarda yani sunucu içerisinde bilgiler saklar. İstediğiniz bilgileri saklayabilirsiniz.


# [1] Flask Uygulama Nesnemizi Başlatıyoruz
# __name__ parametresi, Flask'a şablonları (templates) ve CSS/JS dosyalarını (static) nerede arayacağını söyler.
app = Flask(__name__)


# [2] Uygulama Ayarlarını Config sınıfımızdan yüklüyoruz (Gizli anahtar vb.)
app.config.from_object(Config)

#Bu bir decorator functionudur. Korunmasını istediğimiz rotaların (örneğin; /admin, /admin/courses vb.) üzerine @login_required yazarsak önce bu fonksiyon çalışır eğer oturum ('logged_in' session yoksa) açılmamışsa kullanıcıyı otomatik olarak /login yani (Giriş) sayfasına atar!
def login_required(f):
    @wraps(f) # login_required fonksiyonu hangi sayfanın üstüne yazıldıysa o sayfanın adını içinde saklar ve o sayfanın adını unutmamasını sağlar. Çünkü eğer kontrolden başarılı bir şekilde geçebilirse ozaman o kullanıcıyı gitmek istediği sayfaya tekrar gönderebilmek için.

    # *args, **kwrags: Bu parametreler içeri ne bili gelirse gelsin hepsini içine alan sınırsız bir çanta görevi görür. Kapıda hiçbir eşyayı düşürmeden içeri taşımayı sağlar.

    def decorated_function(*args, **kwrags): # Bu fonksiyon Araya giren bir güvenlik görevlisidir gitmek istediği sayfaya gitmeden önce bu fonksiyon çalışır ve kullanıcının giriş yapıp yapmadığını kontrol eder eğer kullanıcı giriş yapamamışsa kulalnıcıyı sayfanın dışına atar, eğer giriş yapmışsa ozaman geçişine izin verir.
        if "logged_in" not in session:
            flash("Bu Sayfayı Görüntülemek için giriş yapmalısınız.","warning")
            return redirect(url_for("login_page"))
        return f(*args, **kwrags) # Eğer kullanıcı giriş yapmışsa ozaman güvenlik kontrolünden geçtikten sonra tekrar ona eşyalarını geri veriyoruz ve o sayfaya geçiş yapmasına izin veriyoruz
    return decorated_function # Eğer Kullanıcı giriş yapmışsa ozaman güvenlik kontrolünden geçip istediği sayfaya gidebilmesine izin verir o sayfaya yönlendirir ama giriş yapmamışsa ozaman kullanıcıyı login_page sayfasına yönlendirir.


# -------------------------------------------------------------
# 0.5 GİRİŞ (LOGIN) VE ÇIKIŞ (LOGOUT) ROTALARI
# -------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """
    Kullanıcı adı ve şifre sorulan giriş sayfası.
    """
    # Eğer zaten giriş yapmışsa direkt panele yönlendir:
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))

    # strip(): bir metinsel ifadenin başındaki ve sonundaki boşlukları temizler
    if request.method == 'POST':
        kullanici_adi = request.form.get('kullanici_adi', '').strip()
        sifre = request.form.get('sifre', '').strip()
        
        # Veritabanında kontrol edelim
        user = db.check_user_login(kullanici_adi, sifre)
        
        if user:
            # Oturum (Session) başlatılıyor:
            session['logged_in'] = True
            session['user_id'] = user['KullaniciID']
            session['user_name'] = user['AdSoyad']
            session['user_role'] = user['Rol']
            
            flash(f"Hoş geldiniz, {user['AdSoyad']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Hatalı kullanıcı adı veya şifre!", "danger")
            
    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Oturumu kapatır ve tüm bilgileri temizler.
    """
    session.clear()
    flash("Başarıyla çıkış yaptınız.", "info")
    return redirect(url_for('landing_page'))


# -------------------------------------------------------------
# 0. HERKESE AÇIK ÖN YÜZ (LANDING PAGE) ROTASI
# -------------------------------------------------------------
# decorator
@app.route('/')
def landing_page():
    """
    Kullanıcı siteye girdiğinde ilk açılan vitrin (ön yüz) sayfasıdır.
    """
    # Aktif kursları veritabanından çekip ön yüze gönderiyoruz:
    courses = db.get_all_courses()
    return render_template('index.html', courses=courses)


# -------------------------------------------------------------
# 1. YÖNETİM PANELİ ANA SAYFA (DASHBOARD) ROTASI
# -------------------------------------------------------------
@app.route('/admin')
@login_required
def dashboard():
    """
    Kullanıcı siteye girdiğinde ilk açılan yönetim paneli ana sayfasıdır.
    Burada veritabanından istatistikleri ve son eklenen öğrencileri çekeriz.
    """
    # Veritabanından kartlar ve grafikler için özet istatistikleri alıyoruz:
    stats = db.get_dashboard_stats()
    
    # Tabloda göstermek için son öğrencileri çekiyoruz:
    students = db.get_all_students()
    
    # HTML şablonuna (dashboard.html) bu verileri gönderiyoruz:
    return render_template('dashboard.html', stats=stats, students=students[:5], active_page='dashboard')



# -------------------------------------------------------------
# 2. ÖĞRENCİ LİSTELEME VE ARAMA ROTASI
# -------------------------------------------------------------
@app.route('/admin/students')
@login_required
def students_page():
    """
    Tüm öğrencilerin listelendiği, arama yapılabildiği ve yeni öğrenci eklenebildiği sayfa.
    """
    # URL'den arama parametresi gelmiş mi diye bakıyoruz: /students?q=ali
    search_query = request.args.get('q', '')
    
    # Veritabanından öğrencileri ve kurs açılır listesi için kursları çekiyoruz:
    students = db.get_all_students(search_query)
    courses = db.get_all_courses()
    
    return render_template('students.html', students=students, courses=courses, search_query=search_query, active_page='students')



# -------------------------------------------------------------
# 6. KURSLAR SAYFASI VE KURS EKLEME
# -------------------------------------------------------------
@app.route('/admin/courses', methods=['GET', 'POST'])
@login_required
def courses_page():
    """
    Kursların listelendiği ve yeni kurs eklenebildiği sayfa.
    """
    if request.method == 'POST':
        # Yeni kurs formundan verileri alıyoruz:
        kurs_adi = request.form.get('kurs_adi', '').strip()
        egitmen = request.form.get('egitmen', '').strip()
        kredi = request.form.get('kredi', 3)
        kategori = request.form.get('kategori', 'Yazılım')
        
        if kurs_adi and egitmen:
            db.add_course(kurs_adi, egitmen, int(kredi), kategori)
            flash(f'{kurs_adi} kursu başarıyla oluşturuldu!', 'success')
        else:
            flash('Kurs adı ve eğitmen zorunludur!', 'warning')
        return redirect(url_for('courses_page'))

    # Kursları çekip sayfaya gönderiyoruz:
    courses = db.get_all_courses()
    return render_template('courses.html', courses=courses, active_page='courses')

@app.route('/admin/students/add',methods=['POST'])
@login_required
def add_student():
    """
    HTML formundan gönderilen öğrenci bilgilerini yakalayıp veritabanına kaydeder. Form verileri gizli ve güvenli bir şekilde gelsin diye sadece 'POST' isteklerine cevap versin diye ekleme yaptık.
    """

    try:

        ad = request.form.get('ad','').strip()
        soyad = request.form.get('soyad','').strip()
        email = request.form.get('email','').strip()
        telefon = request.form.get('telefon','').strip()
        not_ortalamasi = request.form.get('not_ortalamasi',0)
        kurs_id = request.form.get('kurs_id',0)

        # Basit Bir Validasyon yani veri doğrulama işlemi (Eğer ad veya soyad veya eposta bilgisinden birisi girilmemişse ozaman if in içine girer ve içindeki kodları çalıştırır)
        if not ad or not soyad or not email:
            flash("Lütfen ad,soyad ve e-posta alanlarını boş bırakmayınız!","warning")
            return redirect(url_for("students_page"))

        # Veritabanı fonksiyonumuzu çağırarak öğrenciyi kaydediyoruz.
        db.add_student(ad,soyad,email,telefon,float(not_ortalamasi),int(kurs_id))

        # Kullanıcıya yeşil renkli içinde mesajımızı yazan bir başarı kartı gösteriyoruz
        flash(f'{ad} {soyad} adlı öğrenci başarıyla eklendi!','success')
    
    except Exception as e:
        flash(f"Öğrenci eklenirken bir hata oluştu: {str(e)}",'danger')


    # İşlem bitince kullanıcıyı tekrar öğrenci listesine yönlendiriyoruz
    return redirect(url_for('students_page'))
    
@app.route("/admin/students/edit/<int:student_id>",methods=["POST"])
@login_required
def edit_student(student_id):
    """
    Var olan bir öğrencinin bilgilerini günceller. URL'deki <int:student_id> parçası hangi öğrencinin güncellendiğini belirler. Öğrencinin Id değerini içinde tutar.
    """
    try:
        ad = request.form.get('ad','').strip()
        soyad = request.form.get('soyad','').strip()
        email = request.form.get('email','').strip()
        telefon = request.form.get('telefon','').strip()
        not_ortalamasi = request.form.get('not_ortalamasi',0)
        kurs_id = request.form.get('kurs_id',0)

        db.update_student(student_id,ad,soyad,email,telefon,float(not_ortalamasi),int(kurs_id))
        flash("Öğrenci bilgileri başarıyla güncellendi!","success")
    except Exception as e:
        flash(f"Güncelleme Sırasında hata oluştu: {str(e)}!","danger")

    return redirect(url_for("students_page"))


# Öğrenci Silme
@app.route("/admin/students/delete/<int:student_id>",methods=["POST","GET"])
def delete_student(student_id):
    """
    Seçilen Öğrenciyi veritabanından siler.
    """

    try:
        
        db.delete_student(student_id)
        flash("Öğrenci Kaydı Başarıyla Silindi!","info")

    except Exception as e:
        flash(f"Silme Sırasında hata oluştu: {str(e)}!","danger")

    return redirect(url_for("students_page"))



@app.route('/api/student/<int:student_id>')
def api_get_student(student_id):
    """
    Öğrenci düzenleme modal penceresi açıldığında bilgileri JavaScript ile çekmek için:
    """
    student = db.get_student_by_id(student_id)
    if student:
        return jsonify({"success": True, "student": student})
    return jsonify({"success": False, "message": "Öğrenci bulunamadı"}), 404


# -------------------------------------------------------------
# 8. UYGULAMAYI BAŞLATMA BLOĞU
# -------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)