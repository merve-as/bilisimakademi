
-- Veritabanları içerisinde OgrenciDB isminde bir veritabanı olup olmadığını kontrol ediyoruz. Eğer yoksa if'in içine giriyor ve OgrenciDB ismindeki veritabanını oluşturuyor. Burda bu komutu yazmamızın nedeni o isimde bir veritabanı varsa tekrar veritabanı oluşturma çalışmasın hata almayalım diye, yoksa oluştursun.
DROP TABLE IF EXISTS Ogrenciler;
DROP TABLE IF EXISTS Kullanicilar;
DROP TABLE IF EXISTS Kurslar;

if not exists (select * from sys.databases where name = 'OgrenciDB')
begin

	-- Veritabanı Oluşturur.
	create database OgrenciDB;

end
-- Yukarıdaki işlem tamamlandıktan sonra bir alt satırdaki sonraki komutu çalıştırır.
go

-- Veritabanımızı oluşturduktan sonra veya veritabanımız zaten varsa direkt bundan sonraki yazacağımız sql sorgularının OgrenciDB veritabanı üzerinde çalıştırılmasını sağlar.
use OgrenciDB
go

-- Kurslar isminde bir tablo oluşturur.
create table Kurslar(
-- KursID kolonu int tipinde otomatik olarak artan ve Primary Key olsun
KursID int IDENTITY(1,1) PRIMARY KEY,

-- KursAdi: Boş geçilemez(not null), Türkçe Karakter uyumlu
KursAdi nvarchar(100) not null,

Egitmen nvarchar(100) not null,

-- Kredi: Kursun ders kredisi kolonu (eğer kolona veri kaydedilirken veri yazılmazsa varsayılan olarak 3 değerini alır.)
Kredi int default 3,

Kategori nvarchar(50) default 'Yazılım',

-- OluşturulmaTarihi: Kaydın açıldığı anı SQL server a otomatik kaydeder. GetDate() o anki tarih ve zamanı verir.
OlusturulmaTarihi DateTime default GetDate()

)
go


create table Ogrenciler(

OgrenciID int IDENTITY(1,1) PRIMARY KEY,

Ad nvarchar(50) not null,
Soyad nvarchar(50) not null,

-- Email: Benzersiz olmalı (UNIQUE) iki öğrenci aynı maili kullanamasın
Email nvarchar(100) unique not null,

-- Telefon kolonu isteğe bağlı olsun boş geçilebilsin
Telefon nvarchar(20) null,

-- Not Ortalaması: 0.00 ile 100.00 arası ondalıklı saklamak için decimal
NotOrtalamasi decimal(4,2) default 0.00,
-- KursID: öğrencinin kayıtlı olduğu kursun ID'si (Foreign Key)
KursID int null,

KayitTarihi Datetime default getdate(),

-- Kurslar ve Öğrenci tablosunun ilişki kurulacağı bölüm
--  on delete set null: Bir kurs silinirse öğrenci silinmesin, sadece kursu boş (NULL) kalsın diye on delete set null kısmını ekledik. 

constraint FK_Ogreni_Kurs foreign key (KursID) references Kurslar(KursID) on delete set null


)


create table Kullanicilar(

KullaniciID int IDENTITY(1,1) PRIMARY KEY,
KullaniciAdi nvarchar(50) UNIQUE NOT NULL,
Sifre nvarchar(255) not null,
AdSoyad Nvarchar(100) not null,
Rol nvarchar(20) default 'Admin'

)

-- Kurslar tablosunun içi boş mu diye bakıyoruz eğer içinde veri yoksa veri ekleyeceğiz
if not exists (select 1 from Kurslar)
begin

insert into Kurslar (KursAdi,Egitmen,Kredi,Kategori) values 
('Python & Veritabanı Programlama','Ahmet Hoca',4,'Yazılım'),
('Web Geliştirme (HTML, CSS, JS)','Mehmet Hoca',3,'Tasarım & Web'),
('MS SQL Server İle Veritabanı Yönetimi','Ayşe Hoca',4,'Veritabanı'),
('Yapay Zeka ve Veri Analizi','Can Hoca',5,'Veri Bilimi')
end




-- Öğrenciler tablosunun içi boş mu diye bakıyoruz eğer içinde veri yoksa veri ekleyeceğiz
if not exists (select 1 from Ogrenciler)
begin

insert into Ogrenciler(Ad,Soyad,Email,Telefon,NotOrtalamasi,KursID) values 
('Ali','Yılmaz','ali.yilmaz@email.com','0555 111 22 33',85.50,1),
('Ayşe','Demir','ayse.demir@email.com','0555 222 33 44',92.00,2),
('Mehmet','Kaya','mehmet.kaya@email.com','0555 333 44 55',74.25,1),
('Zeynep','Çelik','zeynep.celik@email.com','0555 444 55 66',88.75,3),
('Burak','Şahin','burak.sahin@email.com','0555 555 66 77',85.50,1),
('Elif','Burçak','elif.burcak@email.com','0555 666 77 88',95.50,4)
end


-- Kullanıcılar tablosunda KullaniciAdi 'admin' bir kullanıcı var mı diye bakıyoruz eğer yoksa  ekliyoruz
if not exists (select * from Kullanicilar where KullaniciAdi = 'admin')
begin

insert into Kullanicilar (KullaniciAdi,Sifre,AdSoyad,Rol)
	values ('admin','123456','Sistem Yöneticisi','Admin')

end
