from ondewo.utils.base_client import BaseClient
from ondewo.utils.base_client_config import BaseClientConfig

from ondewo.t2s.client.services.text_to_speech import Text2Speech
from ondewo.t2s.client.services_container import ServicesContainer


class Client(BaseClient):
    """
    The core python client for interacting with ONDEWO T2S services.
    """

    def _initialize_services(self, config: BaseClientConfig, use_secure_channel: bool) -> None:
        """
        Login with the current config and setup the services in self.services

        Returns:
            None
        """
        self.services: ServicesContainer = ServicesContainer(
            text_to_speech=Text2Speech(config=config, use_secure_channel=use_secure_channel),
        )
