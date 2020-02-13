from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from main.config import *
from PyQt5.QtGui import QPixmap
import requests
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/main.ui', self)
        self.btn_enter.clicked.connect(self.search)

    def search(self):
        text = self.get_text()
        self.request_geocoder_api(text)

    def request_geocoder_api(self, text):
        geocoder_params = {
            "apikey": API_KEY,
            "geocode": text,
            "format": FORMAT
        }
        try:
            response = requests.get(GEOCODER_API_SERVER, params=geocoder_params)
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
            # Координаты центра топонима:
            toponym_coodrinates = toponym["Point"]["pos"]
            # Долгота и широта:
            toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
            delta = "0.07"
            print(delta, toponym_longitude, toponym_lattitude)
            self.request_static_maps_api(delta, toponym_longitude, toponym_lattitude)
        except BaseException:
            self.label.setText('ERROR')

    def request_static_maps_api(self, delta, toponym_longitude, toponym_lattitude):
        map_params = {
            "ll": ",".join([toponym_longitude, toponym_lattitude]),
            "spn": ",".join([delta, delta]),
            "l": "map",
            'pt': f'{",".join([toponym_longitude, toponym_lattitude])},pmwtl'
        }
        try:
            map_api_server = MAP_API_SERVER
            response = requests.get(map_api_server, params=map_params)
            image = response.content
            self.draw_image(image)
        except BaseException:
            self.label.setText('ERROR')

    def draw_image(self, image):
        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(image)
        self.label.setPixmap(QPixmap(map_file))
        print('da')

    def get_text(self):
        return self.textEdit.toPlainText()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
