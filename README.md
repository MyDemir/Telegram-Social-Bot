İşte Telegram Social Bot için güncellenmiş README.md dosyası:


---

Telegram Social Bot

Telegram Social Bot, Twitter, Discord, YouTube ve diğer sosyal medya platformlarındaki içerikleri alıp Telegram'a aktaran bir sistemdir.
Bu bot, belirlediğiniz sosyal medya hesaplarındaki güncellemeleri takip eder ve Telegram grubunuza otomatik olarak iletir. Ayrıca, bir Telegram grubundan diğerine mesajları da aktarabilir.


---

Özellikler:

Twitter'daki belirli kullanıcıların tweetlerini Telegram grubuna aktarır.

Discord'dan Telegram'a mesaj aktarımı sağlar (yakında).

YouTube kanal bildirimlerini Telegram'a gönderir (yakında).

Telegram grupları arasında mesajları kopyalar.



---

Kurulum ve Kullanım

1. Proje Dosyalarını İndirin

Projenizi GitHub'dan indirerek veya git clone komutunu kullanarak projenizi bilgisayarınıza çekebilirsiniz:

git clone https://github.com/kullanici-adi/telegram-social-bot.git
cd telegram-social-bot


---

2. Çevresel Değişkenlerinizi Yapılandırın

Botun çalışabilmesi için .env dosyası üzerinden Telegram bot token'ınızı, chat ID'lerinizi ve takip etmek istediğiniz sosyal medya hesaplarını eklemeniz gerekir.

1. Proje dizininde .env adında bir dosya oluşturun.


2. Aşağıdaki gibi bilgileri doldurun:



# Telegram Bot Token'ınızı ve Chat ID'nizi buraya ekleyin
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
TARGET_CHAT_ID=your_target_chat_id_here

# Twitter Kullanıcısının Adı
TWITTER_USERNAME=elonmusk


---

3. Bağımlılıkları Yükleyin

Botun çalışması için gerekli olan Python bağımlılıklarını yükleyin:

pip install -r requirements.txt


---

4. Botu Çalıştırın

Her şey hazır olduğunda botu çalıştırabilirsiniz:

python bot.py

Bot, Twitter'daki belirlediğiniz kullanıcının tweetlerini otomatik olarak Telegram grubunuza iletmeye başlar.


---

Telegram Grubu Arasında Mesaj Aktarma

Telegram gruplarınız arasında mesaj aktarımı yapabilirsiniz.
Bunun için .env dosyasında TARGET_CHAT_ID değişkenini hedef grubun ID'si ile değiştirmeniz yeterlidir.


---

Sosyal Medya Entegrasyonları (Yakında)

Discord: Discord mesajlarını Telegram'a aktaracak.

YouTube: YouTube kanal bildirimleri ve yeni video yüklemelerini Telegram'a gönderecek.

Reddit: Reddit gönderilerini ve yorumlarını Telegram grubuna aktaracak.



---

Referans Bilgileri

Telegram Bot Token'ınızı Almak İçin:

BotFather ile yeni bir bot oluşturun.

Yeni botunuz için bir token alın ve .env dosyasındaki TELEGRAM_BOT_TOKEN alanına ekleyin.


Telegram Chat ID'nizi Almak İçin:

Botunuzu bir grup sohbetine ekleyin.

Grubun chat ID'sini almak için bu rehberi takip edin.



---

Katkı

Telegram Social Bot projesine katkıda bulunmak için kodu fork edin ve geliştirmelerinizi paylaşın.
Yeni sosyal medya entegrasyonları eklemek isteyenler için pull request'ler her zaman açıktır.


---

Lisans

Bu proje MIT Lisansı ile lisanslanmıştır.


---
