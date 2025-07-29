from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleError, AnsibleParserError

import os
import json
from yandexcloud import SDK
from yandex.cloud.compute.v1.instance_service_pb2 import ListInstancesRequest
from yandex.cloud.compute.v1.instance_service_pb2_grpc import InstanceServiceStub
from yandex.cloud.compute.v1.zone_service_pb2 import ListZonesRequest
from yandex.cloud.compute.v1.zone_service_pb2_grpc import ZoneServiceStub


DOCUMENTATION = r'''
    name: yandex_cloud_inventory
    plugin_type: inventory
    short_description: Yandex.Cloud dynamic inventory using service account key or IAM token
    description:
        - Fetches hosts from Yandex.Cloud Compute using a service account JSON key file or an existing IAM token.
    options:
        plugin:
            description: Name of this plugin
            required: true
            choices: ['yandex_cloud_inventory']
        service_account_key_file:
            description: Path to the service account JSON key file
            required: false
            type: str
        iam_token:
            description: IAM token for authentication (will be used instead of service_account_key_file if provided)
            required: false
            type: str
        folder_id:
            description: Yandex.Cloud folder ID
            required: true
            type: str
        group:
            description: Group name to add all hosts to
            required: false
            type: str
'''

class InventoryModule(BaseInventoryPlugin):
    NAME = 'yandex_cloud_inventory'

    def verify_file(self, path):
        return path.endswith(('yml', 'yaml'))

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path)
        self._read_config_data(path)

        sa_key_file = self.get_option('service_account_key_file')
        iam_token = self.get_option('iam_token')
        folder_id = self.get_option('folder_id')
        group = self.get_option('group')

        # Проверяем входные параметры
        if not folder_id:
            raise AnsibleParserError("Option 'folder_id' is required")
        
        # Проверяем наличие файла сервисного аккаунта
        if sa_key_file and not os.path.isfile(sa_key_file):
            raise AnsibleError(f"Service account key file not found: {sa_key_file}")
        
        # Если нет IAM токена в конфигурации, берем из переменной окружения
        if not iam_token:
            iam_token = os.getenv('YC_IAM_TOKEN')
        
        # Проверяем, что есть хотя бы один способ аутентификации
        if not sa_key_file and not iam_token:
            raise AnsibleParserError("Either 'service_account_key_file', 'iam_token', or 'YC_IAM_TOKEN' environment variable must be provided")

        # Инициализируем SDK с приоритетом: service_account_key_file > iam_token
        try:
            if sa_key_file:
                # Приоритет 1: Сервисный аккаунт
                with open(sa_key_file, 'r') as infile:
                    sa_key = json.load(infile)
                sdk = SDK(service_account_key=sa_key)
            elif iam_token:
                # Приоритет 2: IAM токен
                sdk = SDK(iam_token=iam_token)
            else:
                raise AnsibleError("No authentication method provided")
            
            zone_client = sdk.client(ZoneServiceStub)
            instance_client = sdk.client(InstanceServiceStub)
        except Exception as e:
            raise AnsibleError(f"Failed to initialize Yandex SDK: {e}")

        response = instance_client.List(ListInstancesRequest(folder_id=folder_id))
        instances = response.instances

        # Создаем основную группу, если указана
        if group:
            self.inventory.add_group(group)

        for instance in instances:
            primary_v4 = instance.network_interfaces[0].primary_v4_address

            internal_ip = getattr(primary_v4, 'address', None)
            external_ip = getattr(primary_v4.one_to_one_nat, 'address', None) if primary_v4.one_to_one_nat else None
            
            host_name = instance.name.replace("-", "_")
            zone = instance.zone_id.replace("-", "_")

            labels = {key.replace("-", "_"): value.replace("-", "_") for key, value in instance.labels.items()}

            # Фильтрация: если label ansible == false
            if labels.get('ansible') == 'false':
                continue

            # Добавляем хост
            self.inventory.add_host(host_name)

            ansible_ip = internal_ip if internal_ip else external_ip

            # Назначаем переменные
            self.inventory.set_variable(host_name, 'ansible_host', ansible_ip)
            self.inventory.set_variable(host_name, 'name', instance.name)
            self.inventory.set_variable(host_name, 'ipv4', external_ip)
            self.inventory.set_variable(host_name, 'private_ipv4', internal_ip)
            for key, value in labels.items():
                self.inventory.set_variable(host_name, key, value)  

            # Добавляем в группы
            self.inventory.add_group(zone)
            self.inventory.add_host(host_name, group=zone)

            group_name = labels.get('ansible_group')
            if group_name:
                self.inventory.add_group(group_name)
                self.inventory.add_host(host_name, group=group_name)

            # Добавляем в основную группу, если указана
            if group:
                self.inventory.add_host(host_name, group=group)