import bs4
import requests
import smtplib
from email.mime.text import MIMEText

# Pobranie strony ARMAAG

html = requests.get('https://armaag.gda.pl/komunikat.htm?data=2018-12-18')

# Sparsowanie strony i wyszukanie tabeli z jakoscia powietrza

soup = bs4.BeautifulSoup(html.text, 'html.parser')
tabela = soup.find('table', class_='jakoscpowietrza')

# Sprawdzenie, czy w tabeli znajduja sie informacje o poziomie zoltym lub czerwonym

kolor = tabela.find_all('img')
for i in kolor:
    if 'czerwony' in i['src']:
        alert_status = '<span style="color: red;">czerwony</span>'
        break
    elif 'zolty' in i['src']:
        alert_status = '<span style="color: yellow;">żółty</span>'

# Wyslanie wiadomosci e-mail z ostrzezeniem
# Utworzenie wiadomosci

message = MIMEText('Ostrzeżenie!<br>W Twojej okolicy zarejestrowano podwyzszony poziom smogu!<br>Status alarmu: {}'.format(alert_status), 'html')
message['From'] = 'Stacja badania jakosci powietrza <testowy_tester2018@wp.pl>'
message['To'] = 'tomaszwgdynia@wp.pl'
message['Subject'] = 'Alert smogowy!'

# Wyslanie wiadomosci przez serwer SMTP

smtp = smtplib.SMTP_SSL('smtp.wp.pl', 465)
smtp.ehlo()
smtp.login('testowy_tester2018@wp.pl', 'testtest')
smtp.sendmail(message['From'], message['To'], message.as_string())
smtp.quit()
