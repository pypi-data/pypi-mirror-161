# Latest_IDEarthquake
This package will get the latest earthquake data from BMKG | Meteorological, Climatological, and Geophysical Agency

## How it Works?
This package will scrape from https://www.bmkg.go.id/. 
It will use BeautifulSoup 4 and Request, then produce output in the form of JSON that is ready to be used in web or mobile applications 

## How to Use
```
if __name__ == "__main__" :
    print("Aplikasi Utama")
    result = gempaterkirni.ekstraksi_data()
    gempaterkirni.tampilkan_data(result)
```

## Author
Danahiswara Arifta Majid