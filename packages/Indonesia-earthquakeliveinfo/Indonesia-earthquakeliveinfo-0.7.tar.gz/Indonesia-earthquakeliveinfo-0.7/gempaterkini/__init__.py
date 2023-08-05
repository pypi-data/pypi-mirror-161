import requests
from bs4 import BeautifulSoup


def ekstraksi_data():
    """
    Tanggal: 23 Juli 2022
    Waktu: 14:35:46 WIB
    Magnitudo: 5.7
    Kedalaman: 13 km
    Lokasi: LS=7.57 BT=122.45
    Pusat Gempa: Pusat gempa berada di laut 100 km barat laut Larantuka
    Dirasakan: Dirasakan (Skala MMI): III Ende, III Maumere, III Larantuka, III Lewoleba, II - III Pulau Kalaotoa
    :return:
    """
    try:
        content = requests.get('https://bmkg.go.id')
    except Exception:
        return None
    if content.status_code == 200:
        #200-299 = berhasil, 300-399 =  redirection, 500-599 = server error, 400-499 = client errors,
        soup = BeautifulSoup(content.text, 'html.parser')

        result = soup.find('span',{'class':'waktu'})
        result = result.text.split(', ') #dijadikan array/list
        tanggal = result [0]
        waktu = result [1]

        result = soup.find('div', {'class': 'col-md-6 col-xs-6 gempabumi-detail no-padding'})
        result = result.findChildren('li')
        i = 0
        magnitudo = None
        ls = None
        bt = None
        lokasi = None
        dirasakan = None

        for res in result:
            #print(i, res) -> untuk melihat list dri html
            if i == 1:
                magnitudo = res.text
            elif i == 2:
                kedalaman = res.text
            elif i == 3:
                koordinat = res.text.split(' - ')
                ls = koordinat[0]
                bt = koordinat[1]
            elif i == 4:
                lokasi = res.text
            elif i == 5:
                dirasakan = res.text
            i = i + 1

        hasil = dict()
        hasil['tanggal'] = tanggal #contoh : '23 Juli 2022'
        hasil['waktu'] = waktu #contoh: '14:35:46 WIB'
        hasil['magnitudo'] = magnitudo #contoh :'5.7'
        hasil['kedalaman'] = kedalaman #contoh:'13 Km'
        hasil['koordinat'] = {'ls':ls, 'bt':bt} #contoh: {'ls': 7.57, 'bt': 122.45}]
        hasil['lokasi'] = lokasi
        hasil['dirasakan'] = dirasakan

        return hasil
    else:
        return None


def tampilkan_data(result):
    if result is None:
        print('Tidak bisa menemukan data gempa terkini')
        return
    print('Gempa Terakhir berdasarkan BMKG')
    print(f"Tanggal {result['tanggal']}")
    print(f"Waktu {result['waktu']}")
    print(f"Magnitudo {result['magnitudo']}")
    print(f"Kedalaman {result['kedalaman']}")
    print(f"Lokasi: {result['lokasi']}")
    print(f"Koordinat: LS={result['koordinat']['ls']}, BT={result['koordinat']['bt']}")
    print(f"Dirasakan: {result['dirasakan']}")

if __name__ == '__main__':
    print('Aplikasi utama')
    result = ekstraksi_data()
    tampilkan_data(result)
