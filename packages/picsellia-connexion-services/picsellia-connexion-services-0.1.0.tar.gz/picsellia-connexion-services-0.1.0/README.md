# Picsellia Services

Picsellia Services is a Python library that wraps connexions with Picsellia micro services.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install picsellia-connexion-services.

```bash
pip install picsellia-connexion-services
```

## Usage
### JwtToken
```python
from picsellia_connexion_services.jwt_service import JwtServiceConnexion
service = JwtServiceConnexion({'api_token': '<api_token>', 'deployment_id': '<deployment_id>'}, 'localhost:8000')
service.get('/deployment/{}/stats'.format(deployment_id))
```

## Usage in mocked tests

```python
from picsellia_connexion_services.mocked_service import MockedServiceConnexion
service = MockedServiceConnexion('test')
service.set_next_mocked_response("get", "/ping", JsonResponse({"ok" : True}, status=status.HTTP_200_OK))
service.get("/ping")
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)