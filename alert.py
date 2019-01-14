import bs4
import requests
import smtplib
from email.mime.text import MIMEText

# Wyslanie wiadomosci e-mail z ostrzezeniem


def send_email(wiad):
    # Utworzenie wiadomosci
    # alert_status = 'Ostrzeżenie <span style="color: red;">czerwone</span> dla stacji: '
    # alert_status += ', '.join(red)
    # alert_status += '.<br>Ostrzeżenie <span style="color: yellow;">żółte</span> dla stacji: '
    # alert_status += ', '.join(yel)
    # message = MIMEText('Ostrzeżenie!<br>W Twojej okolicy zarejestrowano podwyzszony poziom smogu!<br>Status alarmu:<br> {}.'.format(alert_status), 'html')
    message = MIMEText(wiad, 'html')
    message['From'] = 'Stacja badania jakosci powietrza <testowy_tester2018@wp.pl>'
    message['To'] = 'ODBIORCA'
    message['Subject'] = 'Alert smogowy!'
    # Wyslanie wiadomosci przez serwer SMTP
    smtp = smtplib.SMTP_SSL('smtp.wp.pl', 465)
    smtp.ehlo()
    smtp.login('testowy_tester2018@wp.pl', 'PASSWORD')
    smtp.sendmail(message['From'], message['To'], message.as_string())
    smtp.quit()
    print('E-mail wysłany!')


# Pobranie strony ARMAAG
link = 'https://armaag.gda.pl/komunikat.htm?data=2018-12-18'
html = requests.get(link)
# html = requests.get('https://armaag.gda.pl/komunikat.htm?data=2019-01-05')

# Sparsowanie strony i wyszukanie tabeli z jakoscia powietrza

soup = bs4.BeautifulSoup(html.text, 'html.parser')
tabela = soup.find('table', class_='jakoscpowietrza')

# Stworzenie listy stacji

stacje = [s.get_text() for s in tabela.find_all('th', class_='tabela_opis3')]
substancje = [s.get_text() for s in tabela.find_all('th', class_='tabela_opis2')]

# Sprawdzenie, czy w tabeli znajduja sie informacje o poziomie zoltym lub czerwonym

kolor = tabela.find_all('img')

alert = []
alerts = []

for c,i in enumerate(kolor):
    if 'czerwony' in i['src']:
        alert.append('<span style="color:red;">{}</span>'.format(substancje[c % 5]))
    elif 'zolty' in i['src']:
        alert.append('<span style="color:#c2c32e;">{}</span>'.format(substancje[c % 5]))
    if c%5 == 4:
        if len(alert) == 0: alert = ['Brak przekroczonych norm']
        alerts.append(alert)
        alert=[]

raport=''
for i, al in enumerate(alerts):
    raport += '{}: {}\n<br>'.format(stacje[i], ', '.join(alerts[i]))

wiadomosc = '<b>Ostrzeżenie o złej jakości powietrza</b>!<br><br>' \
            'W Twojej okolicy zarejestrowano podwyższony poziom smogu!<br>' \
            'Poniżej pełny raport:<br><br>' \
            '{}<br>' \
            'Legenda (% wartości dopuszczalnej):<br>' \
            'Kolor <span style="color:#c2c32e;">żółty</span>: 61-99% wartosci dopuszczalanej<br>' \
            'Kolor <span style="color:red;">czerwony</span>: 100% wartosci dopuszczalnej' \
            '<br><br>' \
            'Źródło: <a href="{}">Fundacja ARMAAG</a>'.format(raport, link)
send_email(wiadomosc)

# if len(alert_red) > 0 or len(alert_yel) > 0:
#     send_email(alert_red, alert_yel)
# else:
#     print('Powietrze jest ok! Nie ma potrzeby wysyłać e-maila z ostrzezeniem.')