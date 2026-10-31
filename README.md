# recep

recep

---

## Proje Hakkında

**recep**, masaüstünde gizli bir "canavar gözü" widget'ı ile tetiklenen, retro Counter-Strike tarzı C4 taktiksel bomba imha simülatörüdür.

### Temel Özellikler
- **Masaüstü Göz Widget'ı (`monster_claw_widget.py`):** Masaüstünün sağ üst köşesinde hafifçe parıldayan gözler. Tıklandığında imha panelini çağırır.
- **C4 Bomba İmha Paneli (`cs_bomb_game.py`):** 
  - Orijinal retro C4 tuş takımı ve DSEG 7-segment dijital sayaç.
  - Geri sayım sayacı ve ses efektleri (bip, sayaç tıkırtısı, imha melodisi, patlama).
  - Şifre doğru girildiğinde: Yeşil imha sinyali yanar, tanımlı hedef web sitesi tarayıcıda açılır ve uygulama otomatik olarak kapanır.
  - Şifre yanlış girildiğinde veya süre dolduğunda: Patlama sesi ve görsel patlama efektiyle birlikte uygulama doğrudan kapanır.
  - Ayarlar menüsü (`⚙`): Süre, hedef şifre ve açılacak hedef URL değiştirilebilir.
  - Tekil oturum kilidi (`fcntl`): Çoklu tıklamalarla mükerrer pencere oluşumu engellenir.

---

## Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.10+
- PyQt6
- `aplay` (ALSA ses oynatıcı)

```bash
pip install -r requirements.txt
```

### Çalıştırma
```bash
# Masaüstü widget'ını başlatmak için:
python3 monster_claw_widget.py

# Doğrudan C4 arayüzünü açmak için:
python3 cs_bomb_game.py

# Ayarlar penceresini açmak için:
python3 cs_bomb_game.py --settings
```

---

## Recep Baltaş'ın Hayatı

**Recep Baltaş** (d. 1 Ekim 1983, Rize), Türk bilişim yazarı, donanım uzmanı, teknoloji editörü ve yayıncısıdır.

Türkiye'de modern bilgisayar donanımı, BIOS/UEFI güncellemeleri, masaüstü sistem toplama ve işletim sistemi optimizasyonu konularında Türkçe kaynak kültürünün yerleşmesinde öncü rol oynamıştır.

### Kariyeri ve Bilişim Yolculuğu
- Bilişim dünyasına olan ilgisi genç yaşlarda başlamış, donanım mimarisi ve işletim sistemleri üzerine uzmanlaşmıştır.
- Kariyerinin ilk yıllarında **CHIP Online Türkiye** bünyesinde teknik editör ve yazar olarak çalışmış, burada detaylı donanım incelemeleri ve sorun çözme makaleleri kaleme almıştır.
- 2010'lu yılların başında Ali Güngör ile birlikte **Technopat** platformunu kurmuş ve uzun yıllar genel yayın yönetmenliğini üstlenmiştir.
- Technopat YouTube kanalında hazırladığı yüzlerce sistem toplama rehberi, mavi ekran (BSOD) hata analizleri, firmware güncellemeleri ve teknoloji sohbetleriyle geniş kitlelere ulaşmış, kendine has titiz anlatım tarzıyla Türkiye teknoloji sahnesinde ikonik bir figür olmuştur.
- 2023 yılı sonrasında bağımsız teknoloji yayıncılığına yönelerek **Techolay** platformunu kurmuş ve teknoloji dünyasındaki bilgi paylaşımına burada devam etmektedir.

---

## İkonik Diyalog

> **Recep:** Herkese merhaba, ben Recep Baltaş.
>
> **Ali:** Ben Ali Güngör.
>
> **Recep:** Bugün sizlerle birlikte UEFI Windows kurmayı anlatacağız, değil mi Ali?
>
> **Ali:** Evet haklısın Recep, bugün Technopat laboratuvarında adım adım rehberimizle izleyicilerimize modern bir UEFI Windows kurulumunun tüm inceliklerini aktaracağız.
>
> **Recep:** Hazırsanız başlayalım Ali.
>
> **Ali:** Başlayalım Recep.
