# pydantic-settings-yaml


Yaml support for Pydantic settings. Load a yaml config file 
as nested Pydantic models. 

Allows to use <file:xxxx> placeholders in the yaml config file
for secrets. A placeholder is replaced with the contents of the
file. Paths are relative to the 'secrets_dir' setting (see below).

## Usage

$cat /config/config.yaml
```
database: 
  password: <file:database_password>
  username: my_database_username
```


$cat /secrets/database_password
```
my_secret_database_password
```


Python code example:
``` 
    from pydantic import BaseModel
    from pydantic_settings_yaml import YamlBaseSettings

    class Database(BaseModel):
        username: str
        password: str


    class Settings(YamlBaseSettings):
        database: Database

        class Config:
            secrets_dir = "/secrets"
            yaml_file = "/config/config.yaml"

    settings = Settings()

    assert settings.dict() == {
        "database": {
            "password": "my_secret_database_password", 
            "username": "my_database_username"
        }
    }
```