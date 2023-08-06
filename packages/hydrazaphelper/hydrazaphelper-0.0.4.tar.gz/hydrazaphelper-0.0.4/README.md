Basic Usage 
```Python
from  hydra_zap_helper.zap_api_manager import ZapManager

if __name__ == "__main__":
    zap_base_url = "http://localhost:9090"
    zap_api_key = "zaproxy"
    zap_path =  'C://projects//HYDRA//reports//zap.html'
    
    manager = ZapManager(zap_base_url, zap_api_key)
    manager.get_report(zap_path)
```
For building wrapper write this command 

This will build all the necessary packages that Python will require.

Also it will create a source distribution

> python setup.py sdist bdist_wheel
