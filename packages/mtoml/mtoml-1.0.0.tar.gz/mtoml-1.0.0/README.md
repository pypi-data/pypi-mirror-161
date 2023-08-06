# mtoml
Manage multiple TOML configurations from a single module.

`pip install mtoml`

[![codefactor](https://www.codefactor.io/repository/github/wuotes/mtoml/badge?style=plastic)](https://www.codefactor.io/repository/github/wuotes/mtoml/) [![circleci](https://circleci.com/gh/wuotes/mtoml.svg?style=shield)](https://app.circleci.com/pipelines/github/wuotes/mtoml) [![codecov](https://codecov.io/gh/wuotes/mtoml/branch/main/graph/badge.svg)](https://codecov.io/gh/wuotes/mtoml) 

```
from mtoml import mtoml

class pets(mtoml):
    def __init__(self):
        mtoml.__init__('.\PATH_TO_CONFIGS\')  # set the relative path to the config directory, defaults to the current directory or a previously set directory

        if not self.is_loaded('dogs'):  # all instances share the same files
            self.load('dogs')  # load a config file named "dogs.toml"

        if not self.is_loaded('cats'):
            self.load('cats')  # load a config file named "cats.toml"

        # this module should not throw any exceptions, if a method fails it returns either False or None.

        self.conf = mtoml('.\PATH_TO_CONFIGS\')  # this is also valid; self.conf.load(), self.conf.is_loaded(), etc

    def __del__(self):
        self.save_all()  # save all loaded configs

    def add_new_dog_breed(self, breed):
        dog_breeds = self.get('dogs', 'breeds')  # gets the current list of dog breeds
        dog_breeds.append(breed)                 # we are assuming it returned a list for brevity but if 'get' fails it returns None
        self.set('dogs', 'breeds', dog_breeds)   # sets the variable 'breeds' in the config 'dogs' to our new list
```