import time
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import os

# --- AYARLAR ---
ARAMA_LISTESI = ["Data Labeling", "Veri Etiketleme", "Image Annotation", "Computer Vision", "Görüntü İşleme","Nesne Tespiti", "Object Detection", "Veri girişi", "Data review"] # Burayı "Image Processing" vb. yapabilirsin
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS') # Google'dan alacağın 'Uygulama Şifresi'
ALICI_POSTA = EMAIL_USER

def ilan_tara():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # Tarayıcıyı gizli açar (üşengeç dostu)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    tum_ilanlar = []
    
    for kelime in ARAMA_LISTESI:
        # LinkedIn URL'sine lokasyon (Turkey) ve Remote filtresi eklenmiş hali
        url = f"https://www.linkedin.com/jobs/search/?keywords={kelime.replace(' ', '%20')}&location=Turkey&f_TPR=r86400"
        driver.get(url)
        time.sleep(3) # Her aramada kısa bekleme
        
        ilanlar = driver.find_elements(By.CLASS_NAME, "base-card__full-link")
        # Her kelime için ilk 3 ilanı al ve listeye ekle
        for i in ilanlar[:3]:
            tum_ilanlar.append(f"{kelime}: {i.get_attribute('href')}")
            
    driver.quit()
    return tum_ilanlar

def mail_at(ilan_listesi):
    if not ilan_listesi:
        print("Bugün yeni ilan yok.")
        return

    msg = EmailMessage()
    msg.set_content("\n".join(ilan_listesi))
    msg['Subject'] = f"Kalk İş Var! - Yeni {ARAMA_LISTESI} İlanları"
    msg['From'] = EMAIL_USER
    msg['To'] = ALICI_POSTA

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
    print("İlanlar e-postana gönderildi!")

# Çalıştır
ilanlar = ilan_tara()
mail_at(ilanlar)
