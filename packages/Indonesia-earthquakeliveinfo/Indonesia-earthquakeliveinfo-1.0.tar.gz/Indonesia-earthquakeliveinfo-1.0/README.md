# Latest Indonesia Earthquake
This package will get the latest earthquake from BMKG | Meteorologica, Climatology, and Geophysical Agency
## HOW IT WORK?
This package will scrape from [BMKG](https://www.bmkg.go.id) to get latest quake happened in indonesia. 

This package will use Beautifulsoup4 and Request, to produce output in the form of JSON that is ready to be used in web or mobile applications

## HOW TO USE
'''
import gempaterkini

if __name__ == '__main__':
    gempa_di_indonesia = gempaterkini.GempaTerkini('https://bmkg.go.id')
    print(f'Aplikasi utama menggunakan package yang memiliki deskripsi {gempa_di_indonesia.description}')
    gempa_di_indonesia.tampilkan_keterangan()
    gempa_di_indonesia.run()
'''



# AUTHOR
Muchamad Faiz
