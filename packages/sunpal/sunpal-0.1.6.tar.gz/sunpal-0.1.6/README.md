# Sunpal
A small demo library for a Sunpal application.

### Installation
```
pip install sunpal
```

### Get started
Write here how start

```Python
import sunpal

# configure
sunpal.configure(SUNPAL_API_KEY, SUNPAL_COMPANY)

```

### Run Tests
```
python3 -m unittest -v tests/customers.py

# Run specific
python3 -m unittest -v tests.interactive.TestCases.test_retrieve
```

### Deploy library
```
# Review and increast version on setup.py
-
# Compile
python3 setup.py sdist bdist_wheel
# Check
twine check dist/*
# Upload
python3 -m twine upload dist/*
```

### Extra only local dev
```
# Set localhost custom domain
export LOCAL_SUNPAL_DOMAIN=localhost:8004
export API_KEY_SUNPAL=
```
