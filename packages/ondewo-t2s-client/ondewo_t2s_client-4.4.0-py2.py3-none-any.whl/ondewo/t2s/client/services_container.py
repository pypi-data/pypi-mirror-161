from dataclasses import dataclass

from ondewo.utils.base_service_container import BaseServicesContainer

from ondewo.t2s.client.services.text_to_speech import Text2Speech


@dataclass
class ServicesContainer(BaseServicesContainer):
    text_to_speech: Text2Speech
