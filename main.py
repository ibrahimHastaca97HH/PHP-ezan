from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

CITIES = {
    9146: "ADANA", 9158: "ADIYAMAN", 9167: "AFYONKARAHISAR", 9185: "AĞRI",
    9193: "AKSARAY", 9198: "AMASYA", 9206: "ANKARA", 9225: "ANTALYA",
    9238: "ARDAHAN", 9246: "ARTVIN", 9252: "AYDIN", 9270: "BALIKESIR",
    9285: "BARTIN", 9288: "BATMAN", 9295: "BAYBURT", 9297: "BILECIK",
    9303: "BINGOL", 9311: "BITLIS", 9315: "BOLU", 9327: "BURDUR",
    9335: "BURSA", 9352: "CANAKKALE", 9359: "CANKIRI", 9370: "CORUM",
    9392: "DENIZLI", 9402: "DIYARBAKIR", 9414: "DUZCE", 9419: "EDIRNE",
    9432: "ELAZIG", 9440: "ERZINCAN", 9451: "ERZURUM", 9470: "ESKISEHIR",
    9479: "GAZIANTEP", 9494: "GIRESUN", 9501: "GUMUSHANE", 9507: "HAKKARI",
    20089: "HATAY", 9522: "IĞDIR", 9528: "ISPARTA", 9541: "ISTANBUL",
    9560: "IZMIR", 9577: "KAHRAMANMARAS", 9581: "KARABUK", 9587: "KARAMAN",
    9594: "KARS", 9609: "KASTAMONU", 9620: "KAYSERI", 9629: "KILIS",
    9635: "KIRIKKALE", 9638: "KIRKLARELI", 9646: "KIRSEHIR", 9654: "KOCAELI",
    9676: "KONYA", 9689: "KUTAHYA", 9703: "MALATYA", 9716: "MANISA",
    9726: "MARDIN", 9737: "MERSIN", 9747: "MUGLA", 9755: "MUS",
    9760: "NEVSEHIR", 9766: "NIGDE", 9782: "ORDU", 9788: "OSMANIYE",
    9799: "RIZE", 9807: "SAKARYA", 9819: "SAMSUN", 9831: "SANLIURFA",
    9839: "SIIRT", 9847: "SINOP", 9854: "SIRNAK", 9868: "SIVAS",
    9879: "TEKIRDAG", 9887: "TOKAT", 9905: "TRABZON", 9914: "TUNCELI",
    9919: "USAK", 9930: "VAN", 9935: "YALOVA", 9949: "YOZGAT", 9955: "ZONGULDAK"
}

def normalize_string(s):
    replacements = str.maketrans("çğıöşü", "cgiosu")
    return s.lower().translate(replacements).upper()

def get_city_id(city_name):
    norm = normalize_string(city_name)
    for id_, name in CITIES.items():
        if name == norm:
            return id_
    return None

def fetch_prayer_times(city_id):
    url = f"https://namazvakitleri.diyanet.gov.tr/tr-TR/{city_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.select_one('#tab-1 > div > table')
    if not table:
        return None

    prayer_times = []
    rows = table.select('tr')
    for row in rows:
        cells = row.select('td')
        if len(cells) >= 8:
            prayer_times.append({
                "miladi_tarih": cells[0].get_text(strip=True),
                "hicri_tarih": cells[1].get_text(strip=True),
                "imsak": cells[2].get_text(strip=True),
                "gunes": cells[3].get_text(strip=True),
                "ogle": cells[4].get_text(strip=True),
                "ikindi": cells[5].get_text(strip=True),
                "aksam": cells[6].get_text(strip=True),
                "yatsi": cells[7].get_text(strip=True),
            })
    return prayer_times

@app.route('/api/ezan', methods=['GET'])
def get_prayer_times():
    city = request.args.get('city', '')
    city_id = get_city_id(city)
    if not city_id:
        return jsonify({'status': False, 'error': 'City not found'}), 404

    data = fetch_prayer_times(city_id)
    if not data:
        return jsonify({'status': False, 'error': 'Prayer times not found'}), 500

    return jsonify({'status': True, 'data': data})

if __name__ == '__main__':
    app.run(debug=True)
