# akerbp.mlpet

Preprocessing tools for Petrophysics ML projects at Eureka

## Installation

- Install the package by running the following (requires python 3.8 or later)

        pip install akerbp.mlpet


## Quick start

- For a short example of how to use the mlpet Dataset class for pre-processing data see below. Please refer to the tests folder of this repository for more examples:

        from akerbp.mlpet import Dataset
        from akerbp.mlpet import utilities

        # Instantiate an empty dataset object using the example settings and mappings provided
        ds = Dataset(
                settings="settings.yaml", # Absolute file paths are preferred
                mappings="mappings.yaml", # Absolute file paths are preferred
                folder_path=r"./", # Absolute file paths are preferred
        )

        # Populate the dataset with data from a file (support for multiple file formats and direct cdf data collection exists)
        ds.load_from_pickle(r"data.pkl") # Absolute file paths are preferred

        # The original data will be kept in ds.df_original and will remain unchanged
        print(ds.df_original.head())

        # Split the data into train-validation sets
        df_train, df_test = utilities.train_test_split(
                df=ds.df_original,
                target_column=ds.label_column,
                id_column=ds.id_column,
                test_size=0.3,
        )

        # Preprocess the data for training according to default workflow
        # print(ds.default_preprocessing_workflow) <- Uncomment to see what the workflow does
        df_preprocessed = ds.preprocess(df_train)


The procedure will be exactly the same for any other dataset class. The only difference will be in the "settings". For a full list of possible settings keys see either the [built documentation](docs/build/html/akerbp.mlpet.html) or the akerbp.mlpet.Dataset class docstring. Make sure that the curve names are consistent with those in the dataset.

The loaded data is NOT mapped at load time but rather at preprocessing time (i.e. when preprocess is called).

## API Documentation

Full API documentaion of the package can be found under the [docs](docs/build/html/index.html) folder once you have run the make html command.

## For developers

- to make the API documentation, from the root directory of the project run (assuming you have installed all development dependencies)

        cd docs/
        make html

- to install mlpet in editable mode for use in another project, there are two
  possible solutions dependent on the tools being used:
   1. If the other package uses poetry, please refer to this [guide](https://github.com/python-poetry/poetry/discussions/1135#discussioncomment-145756)
   2. If you are not using poetry (using conda, pyenv or something else), you will first need to:
      1. Convert the pyproject.toml script to a setup.py file by running the following line:

                curl -Ls https://raw.githubusercontent.com/sdss/flicamera/main/create_setup.py | python3

      2. You can now pip install -e the package in the relevant virtual environment after you have activated it. Note that it might be some conficts with package dependecies when using a conda enviroment.
        You might find it useful to conda install geopandas before pip install -e "conda install -c conda-forge geopandas". In addition, you might need to upgrade pip, setuptools and wheel "python -m pip install --upgrade pip setuptools wheel"
## License

akerbp.mlpet Copyright 2021 AkerBP ASA

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
