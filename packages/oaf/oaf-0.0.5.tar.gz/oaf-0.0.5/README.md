# Oaf

A dumb Python utility to store arbitrary artifacts in any docker image repository

## Install

```sh
pip install oaf
```

## Prerequisites
* Working authentication to your image registry of choice e.g. `~/.docker/config.json`

## Quick Start

Push some files to a docker repository and add labels to the artifact
```python
import oaf

oaf.push("myrepo/foo:v1", file="./tests/data/test.yaml", labels={"qux": "baz"})
```

Pull them back out
```python
oaf.pull("myrepo/foo:v1", "./out/")
```
---

Push an arbitrary python object to a repository
```python
bar_obj = Bar("bar", 1, {"qux": "baz"})

oaf.push("myrepo/bar:v1", obj=bar_obj)
```

Pull the object back out and load it

```python
import jsonpickle 

str_dict = oaf.pull_str("myrepo/bar:v1")
bar_obj = jsonpickle.decode(str_dict["BarObj.json"])
```

---
Push an object in pickle format with a designated filename
```python
oaf.push(
    "myrepo/bar:v2",
    obj_map={"my_obj.pkl": bar_obj},
    obj_encoder=oaf.ObjEncoderType.PICKLE,
)
```

Pull it back out as bytes and load it with pickle
```python
import pickle

byte_dict = oaf.pull_bytes("myrepo/bar:v2")
bar_obj = pickle.loads(byte_dict["test_obj.pkl"])
```

More complete examples can be found in the [tests](./tests/test_api.py)

## FAQ

__What about OCI artifacts?__

OCI artifacts are amazing and will be the future, but many registries don't support them yet, this tool will work with any docker registry. 

Oaf borrows its name from the idea "**O**CI **A**rti**f**acts"


