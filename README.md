# Ansible Yandex Cloud Dynamic Inventory Plugin

Динамический inventory плагин  Ansible для Yandex Cloud, который получает список Compute инстансов и создает inventory на основе зон и меток.

## Возможности

- Получает Compute инстансы из Yandex Cloud
- Поддерживает аутентификацию через IAM токен и ключ сервисного аккаунта
- Создает группы на основе зон и пользовательских меток
- Позволяет исключать инстансы помощью label `ansible: false`
- Поддерживает пользовательские назначения групп через метки

## Установка

### Из исходного кода

1. Клонируйте репозиторий:
```bash
git clone https://github.com/mzatolokin/ansible-yandex-cloud-inventory.git
cd ansible-yandex-cloud-inventory
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Сделайте плагин доступным для Ansible:
```bash
# Вариант 1: Установите переменную окружения
export ANSIBLE_INVENTORY_PLUGINS=./inventory_plugins

# Вариант 2: Добавьте в ansible.cfg
echo "[inventory]" >> ansible.cfg
echo "enable_plugins = yandex_cloud_inventory" >> ansible.cfg
echo "inventory_plugins = ./inventory_plugins" >> ansible.cfg
```

## Конфигурация

### Аутентификация

Плагин поддерживает два метода аутентификации:

#### IAM Токен (Рекомендуется для тестирования)

**⚠️ Важно:** IAM токены действительны только 12 часов и требуют регулярного обновления.

```yaml
plugin: yandex_cloud_inventory
folder_id: ваш-folder-id
iam_token: ваш-iam-токен
```

**Альтернативно**, токен может быть взят из переменной окружения `YC_IAM_TOKEN`:

```yaml
plugin: yandex_cloud_inventory
folder_id: ваш-folder-id
# iam_token будет автоматически взят из переменной окружения YC_IAM_TOKEN
```

**Обновление IAM токена:**
```bash
# Через Yandex Cloud CLI
yc iam create-token

# Или через консоль Yandex Cloud
# https://console.cloud.yandex.ru/iam/security/keys
```

#### Ключ сервисного аккаунта (Рекомендуется)

```yaml
plugin: yandex_cloud_inventory
folder_id: ваш-folder-id
service_account_key_file: /путь/к/файлу/ключа/сервисного/аккаунта.json
```

### Параметры

| Параметр | Обязательный | Описание |
|----------|--------------|----------|
| `plugin` | Да | Должен быть `yandex_cloud_inventory` |
| `folder_id` | Да | ID папки Yandex Cloud |
| `iam_token` | Нет* | IAM токен для аутентификации |
| `service_account_key_file` | Нет* | Путь к JSON файлу ключа сервисного аккаунта |
| `group` | Нет | Имя группы для добавления всех хостов |

*Должен быть предоставлен либо `iam_token`, либо `service_account_key_file`.

### Пример конфигурации

Создайте файл инвентаря (например, `inventory.yml`):

```yaml
plugin: yandex_cloud_inventory
folder_id: <YOUR_FOLDER_ID>
group: ycloud_servers
iam_token: <YOUR_IAM_TOKEN>
```

Или используйте переменную окружения:

```bash
export YC_IAM_TOKEN="ваш-iam-токен"
```

```yaml
plugin: yandex_cloud_inventory
folder_id: <YOUR_FOLDER_ID>
group: ycloud_servers
# iam_token будет взят из переменной окружения YC_IAM_TOKEN
```

## Использование

### Тестирование инвентаря

```bash
ansible-inventory -i inventory.yml --list
```

### Использование с плейбуками Ansible

```bash
ansible-playbook -i inventory.yml playbook.yml
```

### Использование с ansible.cfg

Добавьте в ваш `ansible.cfg`:

```ini
[inventory]
enable_plugins = yandex_cloud_inventory
inventory_plugins = ./inventory_plugins
```

## Группировка инстансов

Плагин автоматически создает группы на основе:

1. **Зоны**: Инстансы группируются по зонам (например, `ru_central1_a`)
2. **Пользовательские группы**: Если у инстанса есть метка `ansible_group`, он добавляется в эту группу
3. **Основная группа**: Если указана, все инстансы добавляются в основную группу

### Поддержка меток

- `ansible: false` - Исключает инстанс из инвентаря
- `ansible_group: имя_группы` - Добавляет инстанс в пользовательскую группу
- Любые другие метки добавляются как переменные хоста

## Требования

- Python 3.8+
- Ansible 2.18.6+
- yandexcloud>=0.99.0


## Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для подробностей.

## Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
5. Отправьте pull request

## Поддержка

По вопросам и проблемам создавайте issue на GitHub.