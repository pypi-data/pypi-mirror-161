import requests
from bs4 import BeautifulSoup


def ekstrak_data():
    """
    Tangggal : 28 Juli 2022
    Waktu : 02:17:36 WIB
    Magnitudo : 4.1
    Kedalaman : 10 km
    Lokasi : 8.20 LS - 115.50 BT
    Pusat Gempa : Pusat gempa berada di darat 16 km barat laut Karangasem
    Dirasakan : Dirasakan (Skala MMI): II Karangasem
    :return:
    """

    try:
        content = requests.get('https://www.bmkg.go.id')
    except Exception:
        return None
    if content.status_code == 200:
        soup = BeautifulSoup(content.text, 'html.parser')
        title = soup.find('title')
        datetime = soup.find('span', {'class': 'waktu'})
        tanggal = datetime.text.split(', ')[0]
        waktu = datetime.text.split(', ')[1]

    result = soup.find('ul', {'class': 'list-unstyled'})
    data = result.findChildren('li')
    wektu = data[0].text
    magnitudo=data[1].text
    kedalaman=data[2].text
    lokasi=data[3].text
    pusat=data[4].text
    dirasakan=data[5].text

    # print(result)



    data_gempa = dict()
    data_gempa['tanggal'] = tanggal
    data_gempa['waktu'] = waktu
    data_gempa['magnitudo'] = magnitudo
    data_gempa['kedalaman'] = kedalaman
    data_gempa['lokasi'] = lokasi
    data_gempa['pusat'] = pusat
    data_gempa['dirasakan'] = dirasakan
    return data_gempa



def show_data(result):
    if result is None:
        print("Tidak ketemu woy")
        return
    print('Data Gempa terakhir BMKG :')
    print(f"Tanggal = {result['tanggal']}")
    print(f"Waktu = {result['waktu']}")
    print(f"Magnitudo = {result['magnitudo']}")
    print(f"Kedalaman = {result['kedalaman']}")
    print(f"Lokasi = {result['lokasi']}")
    print(f"Pusat Gempa = {result['pusat']}")
    print(f"Dirasakan = {result['dirasakan']}")

if __name__ == '__main__':
    print('Package latest gempa')