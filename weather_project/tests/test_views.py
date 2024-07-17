import pytest
from django.urls import reverse
from django.test import Client
import pandas as pd


@pytest.mark.django_db
class TestWeatherViews:

    @pytest.fixture
    def client(self):
        return Client()


    def test_weather_view_get(self, client):
        """
        Тест для проверки GET-запроса к представлению weather_view.
        """
        response = client.get(reverse('weather:weather'))
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'weather_data' not in response.context


    @pytest.mark.parametrize("city", ["ValidCity", "InvalidCity"])
    def test_weather_view_post(self, mocker, client, city):
        """
        Тест для проверки POST-запроса к представлению weather_view с разными городами.
        """
        mock_get_city_coordinates = mocker.patch('weather.views.get_city_coordinates')
        mock_get_weather_data = mocker.patch('weather.views.get_weather_data')
        if city == "ValidCity":
            mock_get_city_coordinates.return_value = (51.5074, -0.1278)
            mock_get_weather_data.return_value = pd.DataFrame({
                "Время": ["00:00", "01:00"],
                "Температура": ["10°C", "11°C"]
            })
        else:
            mock_get_city_coordinates.return_value = (None, None)
            mock_get_weather_data.return_value = pd.DataFrame()
        response = client.post(reverse('weather:weather'), {'city': city})
        assert response.status_code == 200
        if city == "ValidCity":
            assert 'weather_data' in response.context
            assert 'error' not in response.context
        else:
            assert 'error' in response.context
            assert 'weather_data' not in response.context
