
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['tokenup/settings.toml', 'tokenup/.secrets.toml'],
)
