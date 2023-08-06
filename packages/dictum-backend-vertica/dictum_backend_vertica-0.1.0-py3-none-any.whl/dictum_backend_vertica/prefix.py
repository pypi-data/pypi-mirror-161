from packaging import version
from dictum_backend_vertica import __version__

if __name__ == "__main__":
    v = version.parse(__version__)
    print(f"{v.major}.{v.minor}")
