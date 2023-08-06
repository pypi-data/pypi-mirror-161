# `vessl-python-sdk`

## Basic usage

```python
import vessl

vessl.init(organization_name="my-organization")
vessl.create_experiment(...)
```

## Integrations

### Keras

- Use ExperimentCallback

```python
import vessl
from vessl.integration.keras import ExperimentCallback

vessl.init()

# Keras training code
model = Model()
model.compile(...)

# Add integration
model.fit(x, y, epochs=5, callbacks=[ExperimentCallback()])
```

- Run experiment on Vessl using Web UI or SDK


### For M1
```bash
docker context create remote --docker "host=ssh://ec2-user@10.110.3.24"
docker context use remote
docker build . -t vessl-python-sdk
docker run vessl-python-sdk
```
