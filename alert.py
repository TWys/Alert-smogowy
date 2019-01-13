import bs4
import requests
import smtplib
from email.mime.text import MIMEText

# Wyslanie wiadomosci e-mail z ostrzezeniem


def send_email(red, yel):
    # Utworzenie wiadomosci
    alert_status = 'Ostrzeżenie <span style="color: red;">czerwone</span> dla stacji: '
    alert_status += ', '.join(red)
    alert_status += '.<br>Ostrzeżenie <span style="color: yellow;">żółte</span> dla stacji: '
    alert_status += ', '.join(yel)
    message = MIMEText('Ostrzeżenie!<br>W Twojej okolicy zarejestrowano podwyzszony poziom smogu!<br>Status alarmu:<br> {}.'.format(alert_status), 'html')
    message['From'] = 'Stacja badania jakosci powietrza <testowy_tester2018@wp.pl>'
    message['To'] = 'tomaszwgdynia@wp.pl'
    message['Subject'] = 'Alert smogowy!'
    # Wyslanie wiadomosci przez serwer SMTP
    smtp = smtplib.SMTP_SSL('smtp.wp.pl', 465)
    smtp.ehlo()
    smtp.login('testowy_tester2018@wp.pl', 'testtest')
    smtp.sendmail(message['From'], message['To'], message.as_string())
    smtp.quit()
    print('E-mail wysłany!')


# Pobranie strony ARMAAG
html = requests.get('https://armaag.gda.pl/komunikat.htm?data=2018-12-18')

# Sparsowanie strony i wyszukanie tabeli z jakoscia powietrza

soup = bs4.BeautifulSoup(html.text, 'html.parser')
tabela = soup.find('table', class_='jakoscpowietrza')

# Stworzenie listy stacji

stacje = [s.get_text() for s in tabela.find_all('th', class_='tabela_opis3')]
substancje = [s.get_text() for s in tabela.find_all('th', class_='tabela_opis2')]

# Sprawdzenie, czy w tabeli znajduja sie informacje o poziomie zoltym lub czerwonym

kolor = tabela.find_all('img')

alert_red = []
alert_yel = []

for i in kolor:
    if 'czerwony' in i['src']:
        alert_red.append(i.parent.parent.get_text().strip())
    elif 'zolty' in i['src']:
        alert_yel.append(i.parent.parent.get_text().strip())

if len(alert_red) > 0 or len(alert_yel) > 0:
    send_email(alert_red, alert_yel)
else:
    print('Powietrze jest ok! Nie ma potrzeby wysyłać e-maila z ostrzezeniem.')
