# Telegram Social Bot - V2

## Genel Bakış
Telegram Social Bot V2, X (Twitter) platformundan son güncellemeleri Telegram kanalınıza aktaran ve Telegram kanallarında mesaj kopyalama işlemi yapan bir bot olarak tasarlanmıştır. Modüler yapısı sayesinde, gelecekte ek özellikler eklemek ve özelleştirmek kolaydır.

## V2 Özellikleri

### 1. **X (Twitter) Güncellemelerini Telegram Kanalına Aktarma**
- **X (Twitter) Hesabından Son Güncellemeleri Almak**: Bot, kullanıcı adını aldıktan sonra X (Twitter) hesabındaki en son tweetleri çeker.
- **Telegram Kanalına Gönderme**: Alınan tweetlerin metin içeriği ve medya (görseller, videolar) Telegram kanalına iletilir.

### 2. **Telegram Kanalından Hedef Telegram Kanalına Mesaj Kopyalama**
- **Kaynak Kanal ile Hedef Kanallar Arasında Mesaj Kopyalama**: Bot, belirli bir Telegram kanalından mesajları alır ve bunları başka bir hedef Telegram kanalına iletir.
- **Mesajın Kaynağını Belirtme**: Kopyalanan mesajın kaynağını belirtmek amacıyla, mesajın altında kaynağın ismi belirtilir. Böylece kullanıcı, mesajın hangi kanaldan alındığını görebilir.
- **Birden Fazla Hedef Kanal Desteği**: Aynı mesaj birden fazla hedef kanala iletilir.

### 3. **Modüler Yapı**
- **Farklı Dosyalarda İşlevsel Modüller**: Proje, kod karmaşasını engellemek ve daha kolay yönetim sağlamak için modüler hale getirilmiştir. Ana dosya (`main.py`) dışında, X güncellemelerini çeken kod (`x_updates.py`) ve mesajları yönlendiren kod (`telegram_forward.py`) ayrı dosyalarda tutulur.
- **Kolay Özelleştirme**: İleride yapılacak eklemeler ve güncellemeler daha kolay olacak çünkü her fonksiyon kendi dosyasında yer alıyor.

### 4. **Kullanıcı Etkileşimi**
- **Telegram Botu Üzerinden Kullanıcıdan Veri Almak**: Kullanıcıdan X (Twitter) kullanıcı adı ve Telegram kanalından hangi hedef kanala mesaj kopyalanacağı gibi bilgileri almak için bot etkileşimi kullanılır.
- **Seçim Yapma**: Kullanıcı, hangi Telegram kanalından hangi kanallara mesaj göndereceğini seçebilir.

### 5. **Gizli Bilgilerin Yönetimi (.env Dosyası)**
- **API Anahtarları ve Token'lar İçin Güvenli Bir Yapı**: `.env` dosyasında saklanan gizli bilgiler sayesinde API anahtarları ve bot token'ları güvenli bir şekilde yönetilir. `python-dotenv` ile `.env` dosyasındaki veriler okunur.

### 6. **Kolay Dağıtım ve Test**
- **Çeşitli Dağıtım Platformlarında Çalışabilir**: Bot, herhangi bir ücretsiz platformda (örneğin Heroku, Railway, Render, Fly.io) çalışacak şekilde yapılandırılmıştır.
- **Kolay Test ve Güncelleme**: Botu her seferinde manuel olarak güncellemeye gerek kalmadan, gerekli dosyalar tek bir platformda birleştirilerek çalıştırılabilir.

## Sonuç
Telegram Social Bot V2, **X (Twitter)** güncellemelerini Telegram'a yönlendirme, **Telegram kanalından başka bir Telegram kanalına mesaj kopyalama** gibi temel işlevlerin yanı sıra, **modüler yapı**, **bot etkileşimi**, **gizli bilgilerin güvenli yönetimi** ve **kolay dağıtım** imkanı sağlar.

Başka bir özellik eklemek veya düzenleme yapmak için proje kolayca özelleştirilebilir. Bu bot ile Twitter'dan Telegram'a ve Telegram kanallarında mesaj kopyalama işlemleri hızlı ve güvenli bir şekilde yapılabilir.
