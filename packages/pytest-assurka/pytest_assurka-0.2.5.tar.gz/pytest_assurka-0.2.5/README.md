# pytest-assurka: A pytest plugin for Assurka Studio


# Pre-Installation

The api requests use the `requests` package and this may need to be installed first.

```
pip install requests
```

# Installation

pip install the package to your project's virtual environment. Directly from plugin folder:


```bash
pip install -e .
```

or pip install it from Pypi:
```bash
pip install pytest-assurka
```

Activate the plugin with the pytest cli with the command:

```bash
pytest --assurka-projectId={projectId} --assurka-secret={secret} --assurka-testPlanId={testPlanId}
```

You can get the above keys from Assurka Studio https://studio.assurka.io