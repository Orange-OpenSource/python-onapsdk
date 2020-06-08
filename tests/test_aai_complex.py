from unittest import mock

import pytest

from onapsdk.aai.cloud_infrastructure import Complex


COMPLEXES = {
    "complex":[
        {
            "physical-location-id":"integration_test_complex",
            "data-center-code":"1234",
            "complex-name":"integration_test_complex",
            "identity-url":"",
            "resource-version":"1588244056133",
            "physical-location-type":""
            ,"street1":"",
            "street2":"",
            "city":"",
            "state":"",
            "postal-code":"",
            "country":"",
            "region":"",
            "latitude":"",
            "longitude":"",
            "elevation":"",
            "lata":""
        }
    ]
}


@mock.patch.object(Complex, "send_message")
def test_complex(mock_send_message):
    cmplx = Complex(name="test_complex_name",
                    physical_location_id="test_location_id",
                    resource_version="1234")
    assert cmplx.name == "test_complex_name"
    assert cmplx.physical_location_id == "test_location_id"
    assert cmplx.url == (f"{Complex.base_url}{Complex.api_version}/cloud-infrastructure/"
                         "complexes/complex/test_location_id?resource-version=1234")

    cmplx2 = Complex.create(name="test_complex_name",
                            physical_location_id="test_location_id")
    mock_send_message.assert_called_once()    
    assert cmplx2.name == "test_complex_name"
    assert cmplx2.physical_location_id == "test_location_id"
    assert cmplx2.url == (f"{Complex.base_url}{Complex.api_version}/cloud-infrastructure/"
                         "complexes/complex/test_location_id?resource-version=")
    method, _, url = mock_send_message.call_args[0]
    assert method == "PUT"
    assert url == (f"{Complex.base_url}{Complex.api_version}/cloud-infrastructure/"
                   "complexes/complex/test_location_id")


@mock.patch.object(Complex, "send_message_json")
def test_complex_get_all(mock_send_message_json):
    mock_send_message_json.return_value = COMPLEXES
    complexes = list(Complex.get_all())
    assert len(complexes) == 1
    cmplx = complexes[0]
    assert cmplx.name == "integration_test_complex"
    assert cmplx.physical_location_id == "integration_test_complex"
