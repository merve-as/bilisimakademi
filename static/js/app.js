// Mobil Menü Toggle(Açma/Kapatma) Fonksiyonu
function initSidebarToggle() {

    // Hamburger Menü Butonu
    const toggleBtn = document.getElementById('sidebarToggle')
    const sidebar = document.querySelector('.sidebar')

    if(toggleBtn && sidebar){

        toggleBtn.addEventListener("click",function(){
            // show classını ekleyip çıkararak menüyü mobilde veya tablet görünümde gösterip gizliyoru
            sidebar.classList.toggle("show")
        })

        // Sayfa Dışına Tıklandığında Kapanması İçin
        document.addEventListener('click', function(e){
           
            const isClickInsideSidebar = sidebar.contains(e.target)

           const isClickOnToggleBtn = toggleBtn.contains(e.target)

           if(sidebar.classList.contains("show") && !isClickInsideSidebar && !isClickOnToggleBtn){
            sidebar.classList.remove("show")
           }

        })

    }

}

initSidebarToggle()


function initDashboardChart(courseData) {
    
     const canvas = document.getElementById('courseChart');
    if (!canvas || !courseData) return;

    // Python'dan gelen verileri grafik etiketlerine ve sayılarına ayırıyoruz:
    const labels = courseData.map(item => item.kurs);
    const dataCounts = courseData.map(item => item.sayi);

    // Chart.js Çubuk (Bar) Grafiği Başlatma:
    new Chart(canvas.getContext('2d'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Kayıtlı Öğrenci Sayısı',
                data: dataCounts,
                backgroundColor: [
                    'rgba(79, 70, 229, 0.85)',
                    'rgba(16, 185, 129, 0.85)',
                    'rgba(245, 158, 11, 0.85)',
                    'rgba(14, 165, 233, 0.85)'
                ],
                borderColor: [
                    '#4f46e5',
                    '#10b981',
                    '#f59e0b',
                    '#0ea5e9'
                ],
                borderWidth: 1.5,
                borderRadius: 8,
                maxBarThickness: 45
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false // Tek veri grubu olduğu için başlık gizlenebilir
                },
                tooltip: {
                    backgroundColor: '#1e1e2d',
                    padding: 12,
                    cornerRadius: 8
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        font: { family: 'Inter' }
                    },
                    grid: {
                        color: '#f0f2f5'
                    }
                },
                x: {
                    ticks: {
                        font: { family: 'Inter' }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });


}

initDashboardChart()


// Öğrenci Silme İşlemi İçin
function initStudentDeleteButtons(){

    // Sayfadaki class ı bütün btn-delete olan butonları seçer.
    const deleteButtons = document.querySelectorAll('.btn-delete')
    const deleteForm = document.getElementById('deleteStudentForm')


    // if(!deleteButtons.length || !deleteForm) return;


    deleteButtons.forEach(button => {

        button.addEventListener('click',function(){
            const studentId = button.getAttribute('data-id')
            const studentName = button.getAttribute('data-name')

            Swal.fire({
                title:'Emin Misiniz?',
                html: `<strong>${studentName}</strong> adlı öğrenci kaydı kalıcı olarak veritabanından silinecektir!`,
                icon:'warning',
                showCancelButton:true,
                confirmButtonColor: 'red',
                cancelButtonColor: 'gray',
                confirmButtonText: '<i class="fa-solid fa-trash-can me-1"></i> Evet, Sil!',
                cancelButtonText: 'Vazgeç'
            }).then((result)=>{
                if(result.isConfirmed){
                    //Kullanıcı 'Evet, Sil' dediğinde gizli formun adresini ayarlayıp submit ediyoruz yani formu gönderiyoruz
                    deleteForm.action = `/admin/students/delete/${studentId}`
                    deleteForm.submit()
                }
            })

            

        })
    })

}

initStudentDeleteButtons()


// Öğrenci Güncelleme İşlemi İçin
function initStudentEditButtons(){

    // Sayfadaki class ı bütün btn-delete olan butonları seçer.
    const editButtons = document.querySelectorAll('.btn-edit')
    const editModalEl = document.getElementById('editStudentModal')


    if(!editButtons.length || !editModalEl) return;

    const editModal = new bootstrap.Modal(editModalEl)
    const form = document.getElementById('editStudentForm')


    editButtons.forEach(button => {

        button.addEventListener('click',async function(){
            const studentId = button.getAttribute('data-id')

            const gelenCevap = await fetch(`/api/student/${studentId}`)

            const ogrenciBilgileri = await gelenCevap.json()
            if(ogrenciBilgileri.success && ogrenciBilgileri.student){


                    const ogrenci = ogrenciBilgileri.student
                    // Formun gideceği adresi (action) bu öğrencinin ID'sine ayarlıyoruz:
                    form.action = `/admin/students/edit/${studentId}`

                    // Form kutucuklarını gelen verilerle dolduruyoruz:
                    document.getElementById('edit_ad').value = ogrenci.Ad;
                    document.getElementById('edit_soyad').value = ogrenci.Soyad;
                    document.getElementById('edit_email').value = ogrenci.Email;
                    document.getElementById('edit_telefon').value = ogrenci.Telefon || '';
                    document.getElementById('edit_not_ortalamasi').value = ogrenci.NotOrtalamasi;
                    document.getElementById('edit_kurs_id').value = ogrenci.KursID || '';

                    // Modalı ekranda gösteriyoruz:
                    editModal.show();
                } else {
                    Swal.fire('Hata!', 'Öğrenci bilgileri veritabanından getirilemedi.', 'error');
                }
                
        })
    })
}

initStudentEditButtons()