from fastapi.testclient import TestClient
import json
from re import search
from src.rest.app import app

client = TestClient(app)

# REST API calls, that dont provide the expected parameters (Not Found) (countries and wanted_attrib are essential)


def test_no_api_call():
    response = client.get("/")
    assert response.json() == {"detail": "Not Found"}
    assert response.status_code == 404


def test_no_countries_and_attributes():
    response = client.get("/api/data")
    assert response.json() == {"detail": "Not Found"}
    assert response.status_code == 404


def test_no_countries():
    response = client.get("/api/data/Cases/")
    assert response.json() == {"detail": "Not Found"}
    assert response.status_code == 404


def test_no_attributes():
    response = client.get("/api/data/DE/")
    assert response.json() == {"detail": "Not Found"}
    assert response.status_code == 404

# Country Parameter tests


def test_country_not_exist():
    response = client.get("/api/data/NotExist/Cases?lastN=30&bar=True")
    assert response.status_code == 422
    assert search("value is not a valid country", json.dumps(response.json()))


def test_response_okay():
    response = client.get("/api/data/DE/Cases?lastN=30&bar=True")
    assert response.status_code == 200


def test_multiple_countries_okay():
    response = client.get("/api/data/DE,US/Cases?lastN=30&bar=True")
    assert response.status_code == 200


def test_multiple_countries_error():
    response = client.get("/api/data/DE,NotExist/Cases?lastN=30&bar=True")
    assert response.status_code == 422
    assert search("value is not a valid country", json.dumps(response.json()))

# Attributes Parameter tests


def test_false_attribute():
    response = client.get("/api/data/DE/falseAttribute")
    assert response.status_code == 422
    assert search("value is not a valid enumeration member",
                  json.dumps(response.json()))


def test_attribute_okay():
    response = client.get("/api/data/DE/Cases")
    assert response.status_code == 200

# sinceN/lastN Parameter tests
# the test_attribute_okay() test guarantees, that we dont need any of the parameters


def test_sinceN_negative():
    response = client.get("/api/data/DE/Cases?sinceN=-1")
    assert response.status_code == 422
    assert search("value must not be negative", json.dumps(response.json()))


def test_sinceN_okay():
    response = client.get("/api/data/DE/Cases?sinceN=0")
    assert response.status_code == 200


def test_sinceN_notANumber():
    response = client.get("/api/data/DE/Cases?sinceN=N")
    assert response.status_code == 422
    assert search("value is not a valid integer", json.dumps(response.json()))


def test_lastN_negative():
    response = client.get("/api/data/DE/Cases?lastN=-1")
    assert response.status_code == 422
    assert search("value must not be negative", json.dumps(response.json()))


def test_lastN_okay():
    response = client.get("/api/data/DE/Cases?lastN=0")
    assert response.status_code == 200


def test_lastN_notANumber():
    response = client.get("/api/data/DE/Cases?lastN=N")
    assert response.status_code == 422
    assert search("value is not a valid integer", json.dumps(response.json()))

# Log Parameter tests
# We have the evidence from previous tests (e.g. test_sinceN_okay()) that the log parameter is not needed


def test_log_true_okay():
    response = client.get("/api/data/DE/Cases?lastN=0&Log=True")
    assert response.status_code == 200


def test_log_lowerCase_true():
    response = client.get("/api/data/DE/Cases?lastN=0&Log=true")
    assert response.status_code == 200


def test_log_false_okay():
    response = client.get("/api/data/DE/Cases?lastN=0&Log=True")
    assert response.status_code == 200


def test_log_lowerCase_false():
    response = client.get("/api/data/DE/Cases?lastN=0&Log=false")
    assert response.status_code == 200


def test_log_zero_okay():
    response = client.get("/api/data/DE/Cases?lastN=0&Log=0")
    assert response.status_code == 200


def test_log_one_okay():
    response = client.get("/api/data/DE/Cases?lastN=0&Log=1")
    assert response.status_code == 200


def test_log_not_boolean():
    response = client.get("/api/data/DE/Cases?lastN=0&Log=2")
    assert response.status_code == 422
    assert search("value could not be parsed to a boolean",
                  json.dumps(response.json()))

# bar Parameter tests
# We have the evidence from previous tests (e.g. test_sinceN_okay()) that the bar parameter is not needed


def test_bar_true_okay():
    response = client.get("/api/data/DE/Cases?bar=True")
    assert response.status_code == 200


def test_bar_lowerCase_true():
    response = client.get("/api/data/DE/Cases?bar=true")
    assert response.status_code == 200


def test_bar_false_okay():
    response = client.get("/api/data/DE/Cases?bar=False")
    assert response.status_code == 200


def test_bar_lowerCase_false():
    response = client.get("/api/data/DE/Cases?bar=false")
    assert response.status_code == 200


def test_bar_zero_okay():
    response = client.get("/api/data/DE/Cases?bar=0")
    assert response.status_code == 200


def test_bar_one_okay():
    response = client.get("/api/data/DE/Cases?bar=1")
    assert response.status_code == 200


def test_bar_not_boolean():
    response = client.get("/api/data/DE/Cases?bar=N")
    assert response.status_code == 422
    assert search("value could not be parsed to a boolean",
                  json.dumps(response.json()))

# Data source tests


def test_data_source_owid():
    response = client.get("/api/data/DE/Cases?dataSource=OWID")
    assert response.status_code == 200


def test_data_source_ecdc():
    response = client.get("/api/data/DE/Cases?dataSource=ECDC")
    assert response.status_code == 200


def test_data_source_who():
    response = client.get("/api/data/DE/Cases?dataSource=WHO")
    assert response.status_code == 200


def test_data_source_vaccination_but_not_owid():
    response = client.get(
        "/api/data/DE/DailyVaccineDosesAdministered7DayAverage?dataSource=ECDC")
    assert response.status_code == 200
