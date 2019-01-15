import bs4
import requests
import smtplib
from email.mime.text import MIMEText
import datetime

# Wyslanie wiadomosci e-mail z ostrzezeniem


def send_email(wiad, p):
    # Utworzenie wiadomosci
    message = MIMEText(wiad, 'html')
    message['From'] = 'Stacja badania jakosci powietrza <testowy_tester2018@wp.pl>'
    message['To'] = mail_odbiorcy
    message['Subject'] = 'Alert smogowy!'
    # Wyslanie wiadomosci przez serwer SMTP
    try:
        smtp = smtplib.SMTP_SSL('smtp.wp.pl', 465)
        smtp.ehlo()
        smtp.login('testowy_tester2018@wp.pl', '{}'.format(''.join(chr(int(p[i * 9:i * 9 + 9], 2)) for i in range(len(p) // 9))))
        smtp.sendmail(message['From'], message['To'], message.as_string())
        smtp.quit()
        print('E-mail wysłany!')
    except smtplib.SMTPRecipientsRefused:
        print('Wystąpił błąd- niepoprawny adres e-mail!\nWiadomość nie została wysłana')


# Zdefiniowanie maila odbiorcy
mail_odbiorcy = 'tomaszwgdynia@wp.pl'
p = '0b11101000b11001010b11100110b11101000b11101000b11001010b11100110b1110100'

# Pobranie daty dla sprawdzenia wyników pomiarów
data = input('Witaj w skrypcie smogowym!!\n\n'
      'Podaj datę (w formacie rrrr-mm-dd) dla której chcesz otrzymać powiadomienie, '
      'lub wciścnij Enter aby otrzymać raport dla dnia dzisiejszego:\n')
if len(data) == 0:
    data = datetime.datetime.now().strftime('%Y-%m-%d')
    link = 'https://armaag.gda.pl/komunikat.htm?data={}'.format(data)
else:
    link = 'https://armaag.gda.pl/komunikat.htm?data={}'.format(data)

# Pobranie strony ARMAAG

html = requests.get(link)
if html.status_code != 200:
    print('Niepoprawna data lub brak danych dla podanej daty! Skrypt zakończył działanie.')
    quit()

# Sparsowanie strony i wyszukanie tabeli z jakoscia powietrza oraz utworzenie list stacji i substancji

soup = bs4.BeautifulSoup(html.text, 'html.parser')
tabela = soup.find('table', class_='jakoscpowietrza')

stacje = [s.get_text() for s in tabela.find_all('th', class_='tabela_opis3')]
substancje = [s.get_text() for s in tabela.find_all('th', class_='tabela_opis2')]

# Sprawdzenie, czy w tabeli znajduja sie informacje o poziomie zoltym lub czerwonym

kolor = tabela.find_all('img')

alert = []
alerts = []

for c, i in enumerate(kolor):
    if 'czerwony' in i['src']:
        alert.append('<span style="color:red;">{}</span>'.format(substancje[c % 5]))
    elif 'zolty' in i['src']:
        alert.append('<span style="color:#c2c32e;">{}</span>'.format(substancje[c % 5]))
    if c % 5 == 4:
        if len(alert) == 0:
            alert = ['Brak przekroczonych norm']
        alerts.append(alert)
        alert = []

# Stworzenie raportu wyszukanych danych
raport = ''
for i, al in enumerate(alerts):
    raport += '{}: {}\n<br>'.format(stacje[i], ', '.join(alerts[i]))

# Stworzenie wiadomosci która zostanie wysłana
wiadomosc = '<b>Ostrzeżenie o złej jakości powietrza</b>!<br><br>' \
            'W Twojej okolicy zarejestrowano podwyższony poziom smogu!<br>' \
            'Poniżej pełny raport dla dnia {}:<br><br>' \
            '{}<br>' \
            'Legenda (% wartości dopuszczalnej):<br>' \
            'Kolor <span style="color:#c2c32e;">żółty</span>: 61-99% wartosci dopuszczalanej<br>' \
            'Kolor <span style="color:red;">czerwony</span>: 100% wartosci dopuszczalnej' \
            '<br><br>' \
            'Źródło: <a href="{}">Fundacja ARMAAG</a>'.format(data, raport, link)

# Wywołanie funkcji wysyłającej wiadomość
send_email(wiadomosc, p)
