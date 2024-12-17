Nesne Tespiti ve GPS Konum Takibi Uygulaması
Bu proje, kamera görüntüsünde nesne tespiti yaparak, tespit edilen nesnelerin GPS koordinatlarını harita üzerinde işaretlemeyi sağlar. Özellikle insan tespiti yapılır ve bu tespitler kayıt altına alınır.

Projenin Amacı:

Kameradan gelen görüntüde insanları tespit etmek.
Gerçek zamanlı olarak GPS koordinatlarını almak.
Tespit edilen konumları bir harita üzerinde göstermek.
Video kaydı oluşturmak ve ekranda tespit edilen nesneleri işaretlemek.

Kullanılan Teknolojiler:

OpenCV: Kamera görüntüsünü işleme ve nesne tespiti.
YOLO (You Only Look Once): Nesne tespiti algoritması.
Folium: GPS koordinatlarını harita üzerinde göstermek.
Seri Port (Serial): GPS cihazından veri almak.
Python Threading: Aynı anda farklı işlemleri yürütmek.

Proje Nasıl Çalışır?

Kamera Görüntüsü: Bilgisayara bağlı kameradan görüntü alınır.
Nesne Tespiti: YOLO modeli ile görüntüde insanlar tespit edilir.
GPS Verisi: Tespit edilen nesnelerin konum bilgisi, bağlı bir GPS cihazından alınır.
Harita Güncelleme: Tespit edilen konumlar harita üzerinde işaretlenir.
Video Kaydı: İşlenen görüntüler bir video dosyasına kaydedilir.
Gerçek Zamanlı Gösterim: İşlenen görüntü ekranda gösterilir.

Çıktılar:

Tespit edilen nesneler video üzerinde işaretlenir.
drone_map.html dosyası oluşturularak, tespit edilen konumlar haritada gösterilir.
output.avi dosyası oluşturularak video kaydı alınır.

Örnek Kullanım Senaryosu:

Drone veya kamera ile bir alan tarandığında, insan tespiti yapılır.
Tespit edilen kişilerin konumları bir harita üzerinde işaretlenir.
Video kaydı ile yapılan tespitler daha sonra incelenebilir.

Önemli Notlar:

GPS verisi almak için gerçek bir GPS cihazı gereklidir.
Tespit edilen konumlar drone_map.html dosyasına kaydedilir ve tarayıcıda açılarak görüntülenebilir.

Çıktı Dosyaları:

output.avi: Video kaydı.
drone_map.html: Harita üzerinde işaretlenmiş konumlar.
