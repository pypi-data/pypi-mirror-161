def get_urlpatterns(spec):
    from .urls import urlpatterns
    return urlpatterns

def get_config():
    from .apps import APPNAMEConfig
    return APPNAMEConfig
