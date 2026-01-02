📌 Sosyal Ağ Analizi Uygulaması — Proje Raporu
1️⃣ Proje Bilgileri

Ders: Yazılım Geliştirme Laboratuvarı – I
Proje: Proje 2 — Sosyal Ağ Analizi Uygulaması
Bölüm: Bilişim Sistemleri Mühendisliği
Üniversite: Kocaeli Üniversitesi – Teknoloji Fakültesi

👥 Ekip Üyeleri

İbrahim Emir Yıldız — 231307068

Umut Şahin — 231307091

2️⃣ Giriş — Problemin Tanımı ve Amaç

Bu projede kullanıcılar arasındaki sosyal ilişkiler graf veri yapısı kullanılarak modellenmiştir. Düğümler kullanıcıları, kenarlar ise kullanıcılar arasındaki bağlantıları temsil etmektedir. Graf üzerinde çeşitli arama, yol bulma, topluluk analizi ve renklendirme algoritmaları uygulanarak sonuçlar görsel ve tablolar halinde sunulmuştur.

🎯 Projenin Amaçları

Kullanıcı ve bağlantıları dinamik olarak yönetmek

Graf üzerinde erişim ve en kısa yol analizleri yapmak

Ayrık toplulukları ve etkili düğümleri tespit etmek

Welsh–Powell algoritması ile graf renklendirme yapmak

Algoritma ve yazılım tasarım becerilerini geliştirmek

3️⃣ Algoritmalar — Çalışma Mantığı, Akış Diyagramları ve Karmaşıklık
🔷 3.1 BFS (Breadth-First Search)

Amaç: Bir düğümden erişilebilen tüm düğümleri bulma
Yapı: Kuyruk temelli seviye taraması
⏱ Karmaşıklık: O(V + E)
flowchart TD
A[Başla] --> B[Başlangıç düğümü kuyruğa ekle]
B --> C{Kuyruk boş mu?}
C -- Hayır --> D[Kuyruktan düğüm çıkar]
D --> E[Düğümü ziyaret et]
E --> F[Komşuları kontrol et]
F --> G{Ziyaret edilmemiş mi?}
G -- Evet --> H[Kuyruğa ekle ve işaretle]
H --> F
C -- Evet --> I[Bitir]

🔷 3.2 DFS (Depth-First Search)

Amaç: Grafı derinlemesine dolaşmak
Yapı: Özyineleme veya yığın
⏱ Karmaşıklık: O(V + E)

flowchart TD
A[Başla] --> B[Kaynak düğümü ziyaret et]
B --> C[Komşuları kontrol et]
C --> D{Ziyaret edilmemiş komşu var mı?}
D -- Evet --> E[Komşuya git ve DFS çağır]
E --> C
D -- Hayır --> F[Bitir]

🔷 3.3 Dijkstra En Kısa Yol

Amaç: İki düğüm arasındaki en kısa ağırlıklı yolu bulmak
Yapı: Öncelikli kuyruk ile mesafe güncelleme
⏱ Karmaşıklık: O((V + E) log V)

🔷 3.4 A* (A-Star)

Amaç: Heuristik destekli en kısa yol
Formül:

f(n) = g(n) + h(n)

🔷 3.5 Connected Components

Ayrık toplulukların tespiti

Her bileşenin ayrı grup olarak raporlanması

🔷 3.6 Degree Centrality

Her düğümün derece değeri hesaplandı

En etkili düğümler listelendi

🔷 3.7 Welsh–Powell Graf Renklendirme

Düğümler dereceye göre sıralandı

Komşular aynı renge boyanmadı

Minimum renk sayısı sağlandı

4️⃣ Sınıf Yapısı ve Modüller

Uygulama Python OOP yapısı ile geliştirilmiştir.

classDiagram
class Node{
  +id
  +attributes
  +neighbors
}

class Edge{
  +from
  +to
  +weight
}

class Graph{
  +nodes
  +edges
  +add_node()
  +add_edge()
  +load_csv()
  +save_csv()
}

class Algorithms{
  +bfs()
  +dfs()
  +dijkstra()
  +astar()
  +connected_components()
  +centrality()
}

class Coloring{
  +welsh_powell()
}

Graph --> Node
Graph --> Edge
Graph --> Algorithms
Graph --> Coloring

5️⃣ Uygulama – Ekran Görüntüleri, Testler ve Sonuçlar

📂 Veri Saklama

CSV formatı kullanılmaktadır

Düğüm bilgileri, komşuluklar, ağırlıklar saklanmaktadır

🧪 Testler:

Küçük ölçekli graf (10–20 düğüm)

Orta ölçekli graf (50–100 düğüm)

📌 Yapılan analizler:

Çalışma süreleri

Erişim başarı durumları

En kısa yol doğruluk karşılaştırmaları

<img width="1920" height="1080" alt="Ekran görüntüsü 2025-12-31 004236" src="https://github.com/user-attachments/assets/f59f4c65-11c0-4df5-9c74-ae8107d333ec" />
<img width="1920" height="1080" alt="Ekran görüntüsü 2025-12-31 003834" src="https://github.com/user-attachments/assets/c6ef8bf5-1f69-4a72-a468-f26587a224c4" />
<img width="1920" height="1080" alt="Ekran görüntüsü 2025-12-31 003934" src="https://github.com/user-attachments/assets/4f3800e8-e0f2-456a-91aa-6a2f98e95de1" />
<img width="1920" height="1080" alt="Ekran görüntüsü 2025-12-31 004033" src="https://github.com/user-attachments/assets/619b1cbc-3e78-4147-98cc-b54b02f9beb0" />
<img width="1920" height="1080" alt="Ekran görüntüsü 2025-12-31 004118" src="https://github.com/user-attachments/assets/7d731bc8-b279-4654-a77f-a5ec77d4c9b4" />
<img width="1920" height="1080" alt="Ekran görüntüsü 2025-12-31 004200" src="https://github.com/user-attachments/assets/c23afb4b-53fa-4ec0-8be9-a1d8c87c5068" />

6️⃣ Dinamik Ağırlık Hesaplama

Benzer özelliklere sahip düğümler → yüksek ağırlık

Fark arttıkça → ağırlık düşer

Tüm kısa yol algoritmalarında kullanılmaktadır

7️⃣ Sonuç ve Tartışma

✔ Graf veri yapısı başarıyla uygulanmıştır
✔ Farklı algoritmalar test edilmiştir
✔ Kullanıcı etkileşimi ve görselleştirme sağlanmıştır

🔮 Geliştirilebilir Yönler

Daha fazla merkezilik metriği eklenebilir

Daha büyük veri setleri ile performans testleri

Web tabanlı arayüz geliştirme

✅ Sonuç

Bu proje ile sosyal ağ analizi konusunda grafik veri yapıları, algoritmalar ve yazılım tasarımı başarıyla uygulanmış ve görsel olarak kullanıcıya sunulmuştur.




