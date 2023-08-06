import requests
import json
import os
import time
import math
import yaml

from rich.prompt import Prompt
from rich import print
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from rich.progress import (
    TextColumn,
    Progress,
    MofNCompleteColumn,
    SpinnerColumn,
    TimeElapsedColumn,
)

from hashlib import md5


class SW6Shop:

    def __init__(self, target, username=None, password=None, upload_product_images: bool = True):
        os.makedirs('.data/', exist_ok=True)
        self.upload_product_images = upload_product_images
        self.username = username
        self.password = password
        self.target = target
        # looking for config
        if not os.path.exists(f'.data/{target}_shop_config.yaml'):

            print('[yellow][-] No shop config file found. Collecting base data from target shop and creating config...')
            if self.username is None:
                self.username = Prompt.ask('[cyan2] > USERNAME: \n')
            if self.password is None:
                self.password = Prompt.ask('[cyan2] > PASSWORD: \n')
            sales_channel_payload = {
                'filter':
                    [
                        {
                            'type': 'equals',
                            'field': 'name',
                            'value': 'Storefront'
                        },
                    ],
                'associations':
                    {
                        'salesChannels':
                            {
                                'limit': 50,
                            }
                    }
            }
            tax_payload = {
                'filter':
                    [
                        {
                            'type': 'equals',
                            'field': 'taxRate',
                            'value': 19.0
                        },
                    ],
            }
            currency_payload = {
                'filter':
                    [
                        {
                            'type': 'equals',
                            'field': 'isoCode',
                            'value': 'EUR'
                        },
                    ],
            }
            cms_page_payload = {
                'filter':
                    [
                        {
                            'type': 'equals',
                            'field': 'name',
                            'value': 'Standard Produktseite-Layout'
                        },
                    ],
            }
            delivery_time_payload = {
                'filter':
                    [
                        {
                            'type': 'equals',
                            'field': 'name',
                            'value': '1-3 Tage'
                        },
                    ],
            }
            media_folder_payload = {}
            with Progress() as progress:
                progress_task1 = progress.add_task("[magenta bold]Reading shop data...", total=8)
                self.data = self.generate_admin_request(
                    'POST', f'https://{self.target}/api/search/sales-channel-type', payload=sales_channel_payload).json()['included']
                progress.update(progress_task1, advance=1)
                self.tax_id = self.generate_admin_request(
                    'POST', f'https://{self.target}/api/search/tax', payload=tax_payload).json()['data'][0]['id']
                progress.update(progress_task1, advance=1)
                self.currency_id = self.generate_admin_request(
                    'POST', f'https://{self.target}/api/search/currency', payload=currency_payload).json()['data'][0]['id']
                progress.update(progress_task1, advance=1)
                self.product_cms_page_id = self.generate_admin_request(
                    'POST', f'https://{self.target}/api/search/cms-page', payload=cms_page_payload).json()['data'][0]['id']
                progress.update(progress_task1, advance=1)
                self.delivery_time_id = self.generate_admin_request(
                    'POST', f'https://{self.target}/api/search/delivery-time', payload=delivery_time_payload).json()['data'][0]['id']
                progress.update(progress_task1, advance=1)
                self.media_folder_configuration_id = self.generate_admin_request(
                    'POST', f'https://{self.target}/api/search/media-folder-configuration', payload=media_folder_payload).json()['data'][0]
                progress.update(progress_task1, advance=1)

                [self.data.pop(i) for i, val in enumerate(self.data) if val['type'] != 'sales_channel']
                self.data = self.data[0]
                self.sales_channel_id = self.data['id']
                self.attributes = self.data['attributes']
                self.currency_id = self.data['attributes']['currencyId']
                progress.update(progress_task1, advance=1)
                config = {
                    self.target: dict(
                        username=self.username,
                        password=self.password,
                        tax_id=self.tax_id,
                        currency_id=self.currency_id,
                        product_cms_page_id=self.product_cms_page_id,
                        delivery_time_id=self.delivery_time_id,
                        media_folder_configuration_id=self.media_folder_configuration_id,
                        sales_channel_id=self.sales_channel_id,
                    )
                }
                progress.update(progress_task1, advance=1)
            with open(f'.data/{target}_shop_config.yaml', 'w') as configfile:
                yaml.safe_dump(config, configfile)
                progress.update(progress_task1, advance=1)
        else:
            config = yaml.safe_load(open(f'.data/{target}_shop_config.yaml'))
            self.username = config[self.target]['username']
            self.password = config[self.target]['password']
            self.tax_id = config[self.target]['tax_id']
            self.currency_id = config[self.target]['currency_id']
            self.product_cms_page_id = config[self.target]['product_cms_page_id']
            self.delivery_time_id = config[self.target]['delivery_time_id']
            self.media_folder_configuration_id = config[self.target]['media_folder_configuration_id']
            self.sales_channel_id = config[self.target]['sales_channel_id']

    def obtain_access_token(self) -> str[access_token]:
        if os.path.exists('.data/access_token.txt'):
            try:
                data = json.loads(open('.data/access_token.txt', 'r').read())
                access_token = data['access_token']
                timestamp = data['valid_until']
            except json.decoder.JSONDecodeError:
                timestamp = 0

            expired = True if time.time() > timestamp else False
            if not expired:
                return access_token

        else:
            expired = True

        if expired:
            payload = {
                'client_id': 'administration',
                'grant_type': 'password',
                'scopes': 'write',
                'username': self.username,
                'password': self.password
            }

            url = f'https://{self.target}/api/oauth/token'
            response = requests.request('POST', url, json=payload).json()
            token_data = dict(
                access_token=response['access_token'],
                valid_until=time.time() + 590,
            )

        with open('.data/access_token.txt', 'w') as tokenfile:
            tokenfile.write(json.dumps(token_data))

        return token_data['access_token']

    def generate_admin_request(self, method, url, payload=None) -> response_object:
        if payload is None:
            payload = {}

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.obtain_access_token()}',
        }

        response = requests.request(method, url, json=payload, headers=headers)

        return response

    def get_all_products(self) -> list[json_strings]:
        if os.path.exists(f'{self.target} - all products.json'):
            print('[green][+] Reading products from file')
            all_products = json.loads(open(f'{self.target} - all products.json', 'r').read())

        else:

            all_products = []
            i = 100
            payload = {
                'total-count-mode': 1,
                'page': 1,
                'limit': i,
            }

            print(f'[+] getting existing products from {self.target}')
            response = self.generate_admin_request('POST', f'https://{self.target}/api/search/product', payload)
            data = response.json()
            total = data['meta']['total']
            print(f'[+] {total} products found in {self.target}')

            products = data['data']
            all_products.extend(products)
            payload['total-count-mode'] = 0
            pages = math.ceil(total / payload['limit'])

            with Progress(
                    MofNCompleteColumn(),
                    SpinnerColumn(),
                    *Progress.get_default_columns(),
                    TimeElapsedColumn(),
            ) as progress:
                progress_task = progress.add_task("[green bold]Reading products...", total=(pages - 1) * i)
                for page in range(2, pages + 1):
                    payload['page'] = page
                    response = self.generate_admin_request('POST', f'https://{self.target}/api/search/product', payload)
                    data = response.json()
                    products = data['data']
                    all_products.extend(products)
                    progress.update(progress_task, advance=i)

            with open(f'{self.target} - all products.json', 'w') as product_file:
                product_file.write(json.dumps(all_products))

        return all_products

    def get_all_product_ids(self) -> list[json_strings]:
        if os.path.exists(f'{self.target} - all product ids.json'):
            all_products = json.loads(open(f'{self.target} - all product ids.json', 'r').read())

        else:

            all_products = []
            i = 100
            payload = {
                'total-count-mode': 1,
                'page': 1,
                'limit': i,
                "includes": {
                    "product": ["id"]
                }
            }

            print(f'[+] getting existing products from {self.target}')
            response = self.generate_admin_request('POST', f'https://{self.target}/api/search/product', payload)
            data = response.json()
            total = data['meta']['total']
            print(f'[+] {total} products found in {self.target}')

            products = data['data']
            all_products.extend(products)
            payload['total-count-mode'] = 0
            pages = math.ceil(total / payload['limit'])

            with Progress(
                    MofNCompleteColumn(),
                    SpinnerColumn(),
                    *Progress.get_default_columns(),
                    TimeElapsedColumn(),
            ) as progress:
                progress_task = progress.add_task("[green bold]Reading product Ids", total=(pages - 1) * i)
                for page in range(2, pages + 1):
                    payload['page'] = page
                    response = self.generate_admin_request('POST', f'https://{self.target}/api/search/product', payload)
                    data = response.json()
                    products = data['data']
                    all_products.extend(products)
                    progress.update(progress_task, advance=i)

            with open(f'{self.target} - all product ids.json', 'w') as product_file:
                product_file.write(json.dumps(all_products))

        return all_products

    def reduce_prices(self, discount: int) -> None:
        all_products = self.get_all_products()
        id_price_map = {
            x['id']: x['attributes']['price'][0]['gross'] for x in all_products
        }

        factor = 1 - discount / 100

        datas = [
            {
                'id': uuid,
                'price': [
                    {
                        'currencyId': self.currency_id,
                        'gross': math.ceil(price * factor) - 0.1,
                        'net': (math.ceil(price * factor) - 0.1) / 1.19,
                        'linked': True,
                    }
                ],

            } for uuid, price in id_price_map.items()
        ]

        step = s = 100
        chunks = [
            datas[x:x + s] for x in range(0, len(datas), s)
        ]
        with Progress(
                MofNCompleteColumn(),
                SpinnerColumn(),
                *Progress.get_default_columns(),
                TimeElapsedColumn(),
        ) as progress:
            progress_task = progress.add_task("[green bold]Updating product prices", total=len(datas))

            for batch in chunks:
                payload = {
                    "update_prices": {
                        "entity": "product",
                        "action": 'upsert',
                        'payload': batch
                    }
                }

                product_push = self.generate_admin_request('POST', f'https://{self.target}/api/_action/sync', payload)
                progress.update(progress_task, advance=len(batch))

    def create_products(self, datas: list[dict]) -> None:
        """
        create a product with shopware 6 API

        datas is a list of dicts containing payload data
        dict is a data container
        use like:
        for data in datas:

            :data is a dict with the following keys:
                :category: []  # list of categories
                :product_number: ''
                :ean: ''
                :manufacturer_number: ''  # MPN
                :strike_price: ''
                :purchase_price: ''
                :description_html: ''  # main description text
                :description_tail: ''  # main description text, 2nd part
                :short_description: ''  # main short_description text
                :properties: {propery_name: property_value}  # grouping property groups in subgroups TODO
                :manufacturer: ''  # or brand, supplier...
                :manufacturer_image_url: ''
                :name: '' # (or title)
                :children: []  # (['child_data'] list of children-dicts with the following keys:
                    :product_number: ''
                    :ean: ''
                    :manufacturer_number: ''  # MPN
                    :name: ''
                    :description_html: ''  # if child product has its own description
                    :description_tail: ''  # if child product has its own description
                    :strike_price: ''
                    :purchase_price: ''
                    :options: {key:value, key2:value2}  # dict represents key:value pairs for options, e.g. color:red, size:M
                    :images: []  # list of child_image urls

        TODO: check existing products to avoid unnessecery overwriting (not within controller, but within grab main()
        TODO: grouping property groups in subgroups
        TODO: develop property handling and "wesentliche Merkmale" handling
        TODO: add metrics like weight, width, height, shipping methods etc.
        TODO: add reviews writing
        TODO: add better docstring lol
        """
        product_datas = []
        all_product_images = set()
        all_manufacturer_images = {}
        for data in datas:

            full_category = data['category']
            product_number = data['product_number']
            name = data['product_name']
            ean = data['ean']
            description = data['description_html']
            description_tail = data['description_tail']  # if 'description_tail' in data else ''
            short_description = data['short_description']  # if 'short_description' in data else ''
            manufacturer_number = data['manufacturer_number']  # if 'manufacturer_number' in data else ''
            manufacturer_name = data['manufacturer_name']
            manufacturer_image_url = data['manufacturer_image_url']
            strike_price = float(str(data['strike_price']).replace(',', '.'))
            purchase_price = float(str(data['purchase_price']).replace(',', '.'))  # if data['price'] != '' else 0
            energy_class = data['energy_class']  # if 'energy_class' in data else ''
            energy_icon_filename = data['energy_icon_filename']  # if 'energy_icon_filename' in data else ''
            energy_label_filename = data['energy_label_filename']  # if 'energy_label_filename' in data else ''
            energy_pdf_filename = data['energy_pdf_filename']  # if 'energy_datasheet_filename' in data else ''
            image_urls = data['image_urls']
            properties = data['properties']
            children = data['children']

            all_manufacturer_images[manufacturer_name] = manufacturer_image_url
            all_product_images.update(image_urls)
            for child_data in children:
                all_product_images.update(child_data['images'])

            product_id = md5(product_number.encode()).hexdigest()
            manufacturer_media_id = md5(manufacturer_image_url.encode()).hexdigest()

            # images
            product_image_payload_data = [
                {
                    'id': md5((product_id + md5(image_url.encode()).hexdigest()).encode()).hexdigest(),
                    'media': {
                        'id': md5(image_url.encode()).hexdigest(),
                        'mediaFolder':
                            {
                                'id': md5('API Product Media'.encode()).hexdigest(),
                                'name': 'API Product Media',
                                'configurationId': '381fbd435a594aafa817a9c207a77f9f',
                            }
                    },
                    'position': i,
                } for i, image_url in enumerate(image_urls)
            ]

            # categories
            product_category_payload_data = {}
            new_level = product_category_payload_data
            for i, category_name in enumerate(full_category[:-1]):
                category_tree = ''.join(full_category[:i + 1])
                child_category_tree = ''.join(full_category[:i + 2])
                new_level['id'] = md5(category_tree.encode()).hexdigest()
                new_level['name'] = full_category[i]
                new_level['cmsPageId'] = '0c8f4e3f5975446581e996e66528214a'
                new_level['children'] = [
                    {
                        'name': full_category[i + 1],
                        'cmsPageId': '0c8f4e3f5975446581e996e66528214a',
                        'id': md5(child_category_tree.encode()).hexdigest()
                    }
                ]
                new_level = new_level['children'][0]

            custom_fields = {
                'grab_add_short_description': short_description,
                'grab_add_description_tail': description_tail,
                'grab_add_energy_class': energy_class,
                'grab_add_energy_icon_filename': energy_icon_filename,
                'grab_add_energy_label_filename': energy_label_filename,
                'grab_add_energy_datasheet_filename': energy_pdf_filename,
            }
            custom_field_sets_payload_data = [
                {
                    'name': field_name,
                    'id': md5(field_name.encode()).hexdigest(),
                    'type': 'html',
                    'config': {
                        'componentName': "sw-text-editor",
                        'customFieldPosition': 1,
                        'customFieldType': "textEditor",
                        'label': {
                            'en-GB': field_name,
                        }
                    }
                } for field_name in custom_fields
            ]
            custom_fields_payload_data = {name: value for name, value in custom_fields.items()}
            properties_payload_data = [
                {
                    'group':
                        {
                            'id': md5(name.encode()).hexdigest(),
                            'name': name
                        },
                    'id': md5((name + value).encode()).hexdigest(),
                    'name': value
                } for name, value in properties.items()
            ]
            children_payload_data = [
                {
                    'name': child_data['name'],
                    'id': md5(child_data['product_number'].encode()).hexdigest(),
                    'price': [
                        {
                            'currencyId': self.currency_id,
                            'gross': float(str(child_data['purchase_price']).replace(',', '.')),
                            'net': float(str(child_data['purchase_price']).replace(',', '.')) / 1.19,
                            'linked': True,
                            'listPrice':
                                {
                                    'currencyId': self.currency_id,
                                    'gross': float(str(child_data['strike_price']).replace(',', '.')),
                                    'net': float(str(child_data['strike_price']).replace(',', '.')) / 1.19,
                                    'linked': True
                                }
                        }
                    ],
                    'productNumber': child_data['product_number'],
                    'ean': child_data['ean'],
                    'manufacturerNumber': child_data['mpn'],
                    'stock': 1000,
                    'options': [
                        {
                            'group':
                                {
                                    'id': md5(option.encode()).hexdigest(),
                                    'name': option,
                                },
                            'id': md5((option + value).encode()).hexdigest(),
                            'name': value,
                        } for option, value in child_data['options'].items()
                    ],
                    'properties': properties_payload_data,
                    'customFields': {'grab_add_description_tail': child_data['description_tail']},
                    'media': [
                        {
                            'id': md5((md5(child_data['product_number'].encode()).hexdigest() + md5(image_url.encode()).hexdigest()).encode()).hexdigest(),
                            'media': {
                                'id': md5(image_url.encode()).hexdigest(),
                                'mediaFolder':
                                    {
                                        'name': 'Product Images',
                                        'id': md5('Product Images'.encode()).hexdigest(),
                                        'configurationId': '381fbd435a594aafa817a9c207a77f9f',
                                    }
                            },
                            'position': i,
                        } for i, image_url in enumerate(child_data['images'])
                    ],
                    'cover':
                        {
                            'mediaId': md5(child_data['images'][0].encode()).hexdigest(),
                        },
                    'categories': [product_category_payload_data],

                } for child_data in children
            ]
            configurator_settings_payload_data = [
                json.loads(x) for x in set(
                    [
                        json.dumps(
                            {
                                'id': md5((data['product_number'] + value).encode()).hexdigest(),
                                'optionId': md5((option + value).encode()).hexdigest()
                            }
                        ) for child_data in children for option, value in child_data['options'].items()
                    ]
                )
            ]
            configurator_group_config_payload_data = [
                json.loads(x) for x in set(
                    [
                        json.dumps(
                            {
                                'id': md5(option.encode()).hexdigest(),
                                'representation': 'box',
                                # 'expressionForListings': True if option == 'Farbe' else False
                                'expressionForListings': False
                            }
                        ) for child_data in children for option, value in child_data['options'].items()
                    ]
                )
            ]

            product_data = {
                'children': children_payload_data,
                'configuratorSettings': configurator_settings_payload_data,
                'configuratorGroupConfig': configurator_group_config_payload_data,
                'taxId': self.tax_id,
                'stock': 1000,
                'id': product_id,
                'productNumber': product_number,
                'price': [
                    {
                        'currencyId': self.currency_id,
                        'gross': purchase_price,
                        'net': purchase_price / 1.19,
                        'linked': True,
                        'listPrice':
                            {
                                'currencyId': self.currency_id,
                                'gross': strike_price,
                                'net': strike_price / 1.19,
                                'linked': True
                            }
                    }
                ],
                'name': name,
                'properties': properties_payload_data,
                'customFieldSets': [
                    {
                        'name': 'additional_product_data',
                        'id': md5('additional_product_data'.encode()).hexdigest(),
                        'relations': [
                            {
                                'id': md5(f'customFieldSetsProductRelationsadditional_product_data'.encode()).hexdigest(),
                                'entityName': "product"
                            }
                        ],
                        'customFields': custom_field_sets_payload_data
                    },
                ],
                'customFields': custom_fields_payload_data,
                'cmsPageId': self.product_cms_page_id,
                'visibilities': [
                    {
                        'id': md5((product_number + 'visibility').encode()).hexdigest(),
                        'salesChannelId': self.sales_channel_id,
                        'visibility': 30
                    }
                ],
                'ean': ean,
                'deliveryTimeId': self.delivery_time_id,
                'manufacturerNumber': manufacturer_number,
                'description': description,
                'manufacturer': {
                    'name': manufacturer_name,
                    'id': md5(manufacturer_name.encode()).hexdigest(),
                    'media': {
                        'id': manufacturer_media_id,
                        'mediaFolder':
                            {
                                'id': md5('API Manufacurer Media'.encode()).hexdigest(),
                                'name': 'API Manufacurer Media',
                                'configurationId': '381fbd435a594aafa817a9c207a77f9f',
                            }
                    }
                },
                'media': product_image_payload_data,
                'coverId': product_image_payload_data[0]['id'],
                'categories': [product_category_payload_data],
            }

            product_datas.append(product_data)

        payload = {
            "create_product": {
                "entity": "product",
                "action": 'upsert',
                'payload': product_datas
            }
        }

        # upload product
        product_push = self.generate_admin_request('POST', f'https://{self.target}/api/_action/sync', payload)
        product_resp_data = json.loads(product_push.text) if product_push.text != '' else 'no response => success'

        # upload product images
        if self.upload_product_images:
            all_product_images = set(all_product_images)
            tasks = []
            with ThreadPoolExecutor(max_workers=12) as executor:

                for i, image_url in enumerate(all_product_images):
                    # fileextension = image_url.split('.')[-1]
                    tasks.append(
                        executor.submit(
                            self.generate_admin_request,
                            'POST',
                            f'https://{self.target}/api/_action/media/{md5(image_url.encode()).hexdigest()}'
                            f'/upload?extension=webp&fileName={product_number}_Produktbild_{i + 1}',
                            {'url': image_url}
                        )
                    )

        # upload manufacturer images

        for name, url in all_manufacturer_images.items():
            manufacturer_media_id = md5(url.encode()).hexdigest()
            manufacturer_image_payload = {'url': url}
            manufacturor_media_push = self.generate_admin_request(
                'POST', f'https://{self.target}/api/_action/media/{manufacturer_media_id}/upload?extension=webp&fileName={name}_Herstellerbild',
                manufacturer_image_payload)

        manufacturor_resp_data = json.loads(manufacturor_media_push.text) if manufacturor_media_push.text != '' else 'no response => success'

        return product_resp_data, manufacturor_resp_data

    def delete_all_products(self) -> None:
        all_products = self.get_all_product_ids()

        all_ids = [{"id": x['id']} for x in all_products]
        i = 100
        chunks = [all_ids[x:x + i] for x in range(0, len(all_ids), i)]

        # with ThreadPoolExecutor() as executor:
        #     with Progress() as progress:
        #         progress_task = progress.add_task("[red bold]Deleting products...", total=len(all_ids))
        #
        #         tasks = [
        #             executor.submit(
        #                 self.generate_admin_request,
        #                 'DELETE',
        #                 f'https://{self.target}/api/product/{id}')
        #             for id in all_ids
        #         ]
        #
        #         [progress.update(progress_task, advance=1) for _ in futures.as_completed(tasks)]
        with Progress(
                MofNCompleteColumn(),
                SpinnerColumn(),
                *Progress.get_default_columns(),
                TimeElapsedColumn(),
        ) as progress:
            progress_task = progress.add_task("[red bold]Deleting products", total=len(chunks))
            for batch in chunks:
                payload = {
                    'delete_products': {
                        "action": "delete",
                        "entity": "product",
                        "payload": batch,
                    },
                }
                response = self.generate_admin_request('POST', f'https://{self.target}/api/_action/sync', payload)
                if response.status_code != 200:
                    print(response)
                progress.update(progress_task, advance=1)

    def edit_cms_pages(self, sites_contents: dict[site_name: html_content]) -> None:

        with Progress(
                TextColumn("[yellow][+]"),
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                SpinnerColumn(),
        ) as progress:
            progress.add_task('[yellow]Reading CMS pages...')

            pages_payload = {
                'associations': {
                    'sections': {
                        'associations': {
                            'blocks': {
                                'associations': {
                                    'slots': {}
                                }
                            }
                        }
                    }
                }
            }
            url = f'https://{self.target}/api/search/cms-page'
            response = self.generate_admin_request('POST', url, payload=pages_payload).json()
            result = response
            pages = result['data']
            sections = [line for line in result['included'] if line['type'] == 'cms_section']
            blocks = [line for line in result['included'] if line['type'] == 'cms_block']
            slots = [line for line in result['included'] if line['type'] == 'cms_slot']

            for content in pages:
                for name in sites_contents.keys():
                    for value in content['attributes'].values():
                        if name.lower() in str(value).lower():
                            sites_contents[name]['id'] = content['id']

            for name, value in sites_contents.copy().items():
                if 'id' not in value:
                    del sites_contents[name]

            for name, value in sites_contents.items():
                for section in sections:
                    if value['id'] == section['attributes']['pageId']:
                        sites_contents[name]['section_id'] = section['id']

            for name, value in sites_contents.items():
                for block in blocks:
                    if value['section_id'] == block['attributes']['sectionId'] and block['attributes']['position'] == 0:
                        sites_contents[name]['block_id'] = block['id']

            for name, value in sites_contents.items():
                for slot in slots:
                    if value['block_id'] == slot['attributes']['blockId']:
                        sites_contents[name]['slot_id'] = slot['id']

        with Progress() as progress:
            task = progress.add_task('[yellow][+] Uploading CMS content', total=sites_contents.__len__())
            responses = []
            for name, data in sites_contents.items():
                patch_payload = {
                    "id": data['id'],
                    "sections": [
                        {
                            "id": data['section_id'],
                            "blocks": [
                                {
                                    "id": data['block_id'],
                                    "slots": [
                                        {
                                            "id": data['slot_id'],
                                            "config": {
                                                "content": {
                                                    "source": "static",
                                                    "value": data['content']
                                                }
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
                response = self.generate_admin_request('PATCH', f'https://{self.target}/api/cms-page/{data["id"]}', payload=patch_payload)
                responses.append(response)
                progress.update(task, advance=1)

        return responses

    def edit_snippets(self, snippets_contents: dict[snippet_name: html_content]) -> None:

        with Progress(
                TextColumn("[yellow][+]"),
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                SpinnerColumn(),
        ) as progress:
            progress.add_task('[yellow]Reading snippets...')
            payload = {
                'limit': 100,
                'filter': [
                    {
                        'type': 'multi',
                        'operator': 'or',
                        'queries': [
                            {
                                'type': 'equals',
                                'field': 'translationKey',
                                'value': name,
                            } for name in snippets_contents.keys()
                        ],
                    },
                ],
                'associations': {
                    'set': {}
                }
            }
            url = f'https://{self.target}/api/search/snippet'
            response = self.generate_admin_request('POST', url, payload)
            result = response.json()
            snippets = result['data']
            snippet_sets = result['included']
            for snippet_set in snippet_sets:
                if snippet_set['attributes']['name'] == 'BASE de-DE':
                    snippet_set_id = snippet_set['id']

            for snippet in snippets:
                for name, value in snippets_contents.items():
                    if name == snippet['attributes']['translationKey'] and snippet_set_id == snippet['attributes']['setId']:
                        value['id'] = snippet['id']

        with Progress() as progress:
            task = progress.add_task('[yellow][+] Uploading CMS content', total=snippets_contents.__len__())

            for snippet in snippets_contents.values():
                # update snippet
                payload = {
                    'value': snippet['content'],
                }
                url = f'https://{self.target}/api/snippet/{snippet["id"]}'
                response = self.generate_admin_request('PATCH', url, payload)
                resp = json.loads(response.text) if response.text != '' else 'no response => success'
                progress.update(task, advance=1)


# def obtain_access_token(target, username, password):
#     if os.path.exists('access_token.txt'):
#         try:
#             data = json.loads(open('access_token.txt', 'r').read())
#             access_token = data['access_token']
#             timestamp = data['valid_until']
#         except json.decoder.JSONDecodeError:
#             timestamp = 0
#
#         expired = True if time.time() > timestamp else False
#         if not expired:
#             return access_token
#
#     else:
#         expired = True
#
#     if expired:
#         payload = {
#             'client_id': 'administration',
#             'grant_type': 'password',
#             'scopes': 'write',
#             'username': username,
#             'password': password
#         }
#
#         url = f'https://{target}/api/oauth/token'
#         response = requests.request('POST', url, json=payload).json()
#         token_data = dict(
#             access_token=response['access_token'],
#             valid_until=time.time() + 590,
#         )
#
#         with open('access_token.txt', 'w') as tokenfile:
#             tokenfile.write(json.dumps(token_data))
#
#         return token_data['access_token']


# def generate_admin_request(method, url, target, username, password, payload=None):
#     if payload is None:
#         payload = {}
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': f'Bearer {obtain_access_token(target, username, password)}',
#     }
#
#     response = requests.request(method, url, headers=headers, json=payload)
#
#     return response
#
#
# def get_all_products(target, username, password):
#     if os.path.exists(f'{target} - all products.json'):
#
#         all_products = json.loads(open(f'{target} - all products.json', 'r').read())
#
#     else:
#
#         all_products = []
#         payload = {
#             'total-count-mode': 1,
#             'page': 1,
#             'limit': 10,
#         }
#
#         print(f'getting existing products from {target}')
#         response = generate_admin_request('POST', f'https://{target}/api/search/product', target, username, password, payload)
#         data = response.json()
#         total = data['meta']['total']
#         print(f'{total} products found in {target}')
#         products = data['data']
#         all_products.extend(products)
#         payload['total-count-mode'] = 0
#         pages = math.ceil(total / payload['limit'])
#         for page in range(2, pages + 1):
#             payload['page'] = page
#             response = generate_admin_request('POST', f'https://{target}/api/search/product', username, password, payload)
#             data = response.json()
#             products = data['data']
#             all_products.extend(products)
#             print(f'page {page}/{pages} done')
#
#         with open(f'{target} - all products.json', 'w') as product_file:
#             product_file.write(json.dumps(all_products))
#
#         return all_products

# def delete_images_with_no_folder(target, username, password):
#     all_images = []
#     payload = {
#         'total-count-mode': 1,
#         'page': 1,
#         'limit': 100,
#     }
#     response = generate_admin_request('POST', f'https://{target}/api/search/media', username, password, payload)
#     data = response.json()
#     total = data['meta']['total']
#     images = data['data']
#     all_images.extend(images)
#     payload['total-count-mode'] = 0
#     pages = math.ceil(total / payload['limit'])
#     for page in range(2, pages + 1):
#         payload['page'] = page
#         response = generate_admin_request('POST', f'https://{target}/api/search/media', password, password, payload)
#         data = response.json()
#         images = data['data']
#         all_images.extend(images)
#         print(f'page {page}/{pages} done')
#
#     no_folder_ids = [x['id'] for x in all_images if x['attributes']['mediaFolderId'] is None]
#
#     tasks = []
#     with ThreadPoolExecutor(max_workers=10) as executor:
#         tasks = []
#         for uuid in no_folder_ids:
#             tasks.append(executor.submit(generate_admin_request, 'DELETE', f'https://{target}/api/media/{uuid}', password, password))
#
#         for job in futures.as_completed(tasks):
#             print(f'{job} deleted')
#
#     # for uuid in no_folder_ids:
#     #     response = generate_admin_request('DELETE', f'https://{HOST}/api/media/{uuid}', password, password)
#     #     print(f'{uuid} deleted')
#
#     return response
#
#
# def delete_all_products(target, username, password):
#     all_products = get_all_products(target, username, password)
#     all_manufacturers = set(x['attributes']['manufacturerId'] for x in all_products)
#     all_ids = [{"id": x['id']} for x in all_products]
#
#     chunks = [all_ids[x:x + 100] for x in range(0, len(all_ids), 100)]
#
#     for batch in chunks:
#         payload = {
#             'delete_products': {
#                 "action": "delete",
#                 "entity": "product",
#                 "payload": batch,
#             },
#             # 'delete_manufacturers': {
#             #     "action": "delete",
#             #     "entity": "product_manufacturer",
#             #     "payload": [
#             #         {
#             #             'id': uuid
#             #         } for uuid in all_manufacturers
#             #     ],
#             # }
#         }
#         response = generate_admin_request('POST', f'https://{target}/api/_action/sync', password, password, payload)
#
#         print('ok')
#
#
# def get_products_with_empty_media(target, username, password):
#     empty_media_products = []
#     payload = {
#         'total-count-mode': 1,
#         'page': 1,
#         'limit': 100,
#         "filter": [
#             {
#                 'field': "media.id",
#                 'type': "equals",
#                 'value': None,
#             }
#         ]
#     }
#
#     response = generate_admin_request('POST', f'https://{target}/api/search/product', username, password, payload)
#     data = response.json()
#     total = data['meta']['total']
#     product_numbers = [
#         p['attributes']['productNumber'] for p in data['data']
#     ]
#     empty_media_products.extend(product_numbers)
#     payload['total-count-mode'] = 0
#     pages = math.ceil(total / payload['limit'])
#     for page in range(2, pages + 1):
#         payload['page'] = page
#         response = generate_admin_request('POST', f'https://{target}/api/search/product', password, password, payload)
#         data = response.json()
#         product_numbers = [
#             p['attributes']['productNumber'] for p in data['data']
#         ]
#         empty_media_products.extend(product_numbers)
#         print(f'page {page}/{pages} done')
#
#
# def create_product(data, target, username, password):
#     """
#     create a product with shopware 6 API
#
#     :data is a dict with keys:
#         :category: []  # list of categories
#         :product_number: ''
#         :ean: ''
#         :manufacturer_number: ''  # MPN
#         :strike_price: ''
#         :purchase_price: ''
#         :description_html: ''  # main description text
#         :description_tail: ''  # main description text, 2nd part
#         :short_description: ''  # main short_description text
#         :properties: {propery_group: property_value}  # grouping property groups in subgroups TODO
#         :manufacturer: ''  # or brand, supplier...
#         :manufacturer_image_url: ''
#         :name: '' # (or title)
#         :children: []  # (['child_data'] list of children-dicts with the following keys:
#             :product_number: ''
#             :name: ''
#             :description_html: ''  # if child product has its own description
#             :description_tail: ''  # if child product has its own description
#             :price: float
#             :ean: ''
#             :options: [{}, {}]  # list of dicts where a dict represents a key:value for options, e.g. color:red
#             :images: []  # list of child_image urls
#
#     TODO: check existing products to avoid unnessecery overwriting (not within controller, but within grab main()
#     TODO: grouping property groups in subgroups
#     TODO: develop property handling and "wesentliche Merkmale" handling
#     TODO: add metrics like weight, width, height etc.
#     TODO: add reviews
#     TODO: add better docstring lol
#     """
#
#     full_category = data['category']
#     product_number = data['product_number']
#     name = data['product_name']
#     ean = data['ean']
#     description = data['description_html']
#     description_tail = data['description_tail']  # if 'description_tail' in data else ''
#     short_description = data['short_description']  # if 'short_description' in data else ''
#     manufacturer_number = data['manufacturer_number']  # if 'manufacturer_number' in data else ''
#     manufacturer_name = data['manufacturer_name']
#     manufacturer_image_url = data['manufacturer_image_url']
#     price = float(str(data['price']).replace(',', '.'))  # if data['price'] != '' else 0
#     energy_class = data['energy_class']  # if 'energy_class' in data else ''
#     energy_icon_filename = data['energy_icon_filename']  # if 'energy_icon_filename' in data else ''
#     energy_label_filename = data['energy_label_filename']  # if 'energy_label_filename' in data else ''
#     energy_datasheet_filename = data['energy_datasheet_filename']  # if 'energy_datasheet_filename' in data else ''
#     image_urls = data['image_urls']
#     properties = data['properties']
#     children = data['children']
#
#     product_id = md5(product_number.encode()).hexdigest()
#     manufacturer_media_id = md5(manufacturer_image_url.encode()).hexdigest()
#
#     # images
#
#     product_image_payload_data = [
#         {
#             'id': md5((product_id + md5(image_url.encode()).hexdigest()).encode()).hexdigest(),
#             'media': {
#                 'id': md5(image_url.encode()).hexdigest(),
#                 'mediaFolder':
#                     {
#                         'id': md5('API Product Media'.encode()).hexdigest(),
#                         'name': 'API Product Media',
#                         'configurationId': '381fbd435a594aafa817a9c207a77f9f',
#                     }
#             },
#             'position': i,
#         } for i, image_url in enumerate(image_urls)
#     ]
#
#     # categories
#     product_category_payload_data = {}
#     new_level = product_category_payload_data
#     for i, category_name in enumerate(full_category[:-1]):
#         category_tree = ''.join(full_category[:i + 1])
#         child_category_tree = ''.join(full_category[:i + 2])
#         new_level['id'] = md5(category_tree.encode()).hexdigest()
#         new_level['name'] = full_category[i]
#         new_level['cmsPageId'] = '0c8f4e3f5975446581e996e66528214a'
#         new_level['children'] = [
#             {
#                 'name': full_category[i + 1],
#                 'cmsPageId': '0c8f4e3f5975446581e996e66528214a',
#                 'id': md5(child_category_tree.encode()).hexdigest()
#             }
#         ]
#         new_level = new_level['children'][0]
#
#     custom_fields = {
#         'grab_add_short_description': short_description,
#         'grab_add_description_tail': description_tail,
#         'grab_add_energy_class': energy_class,
#         'grab_add_energy_icon_filename': energy_icon_filename,
#         'grab_add_energy_label_filename': energy_label_filename,
#         'grab_add_energy_datasheet_filename': energy_datasheet_filename,
#     }
#     custom_field_sets_payload_data = [
#         {
#             'name': field_name,
#             'id': md5(field_name.encode()).hexdigest(),
#             'type': 'html',
#             'config': {
#                 'componentName': "sw-text-editor",
#                 'customFieldPosition': 1,
#                 'customFieldType': "textEditor",
#                 'label': {
#                     'en-GB': field_name,
#                 }
#             }
#         } for field_name in custom_fields
#     ]
#     custom_fields_payload_data = {x: custom_fields[x] for x in custom_fields}
#     properties_payload_data = [
#         {
#             'group':
#                 {
#                     'id': md5(property_name.encode()).hexdigest(),
#                     'name': property_name
#                 },
#             'id': md5((property_name + properties[property_name]).encode()).hexdigest(),
#             'name': properties[property_name]
#         } for property_name in properties
#     ]
#     children_payload_data = [
#         {
#             'name': child_data['name'],
#             'id': md5(child_data['product_number'].encode()).hexdigest(),
#             'price': [
#                 {
#                     'currencyId': 'b7d2554b0ce847cd82f3ac9bd1c0dfca',
#                     'gross': float(child_data['price'].replace(',', '.')),
#                     'net': float(child_data['price'].replace(',', '.')) / 1.19,
#                     'linked': True
#                 }
#             ],
#             'productNumber': child_data['product_number'],
#             'stock': 999,
#             'options': [
#                 {
#                     'group':
#                         {
#                             'id': md5(option.encode()).hexdigest(),
#                             'name': option,
#                         },
#                     'id': md5((option + value).encode()).hexdigest(),
#                     'name': value,
#                 } for options in child_data['options'] for option, value in options.items()
#             ],
#             'properties': properties_payload_data,
#             'media': [
#                 {
#                     'id': md5((md5(child_data['product_number'].encode()).hexdigest() + md5(image_url.encode()).hexdigest()).encode()).hexdigest(),
#                     'media': {
#                         'id': md5(image_url.encode()).hexdigest(),
#                         'mediaFolder':
#                             {
#                                 'name': 'Product Images',
#                                 'id': md5('Product Images'.encode()).hexdigest()
#                             }
#                     },
#                     'position': i,
#                 } for i, image_url in enumerate(child_data['images'])
#             ],
#             'cover':
#                 {
#                     'mediaId': md5(child_data['images'][0].encode()).hexdigest(),
#                 }
#         } for child_data in children
#     ]
#     configurator_settings_payload_data = [
#         json.loads(x) for x in set(
#             [
#                 json.dumps(
#                     {
#                         'id': md5((data['product_number'] + value).encode()).hexdigest(),
#                         'optionId': md5((option + value).encode()).hexdigest()
#                     }
#                 ) for child_data in children for options in child_data['options'] for option, value in options.items()
#             ]
#         )
#     ]
#     configurator_group_config_payload_data = [
#         json.loads(x) for x in set(
#             [
#                 json.dumps(
#                     {
#                         'id': md5(option.encode()).hexdigest(),
#                         'representation': 'box',
#                         'expressionForListings': False if option == 'Farbe' else False
#                     }
#                 ) for child_data in children for options in child_data['options'] for option, value in options.items()
#             ]
#         )
#     ]
#
#     product_data = {
#         'children': children_payload_data,
#         'configuratorSettings': configurator_settings_payload_data,
#         'configuratorGroupConfig': configurator_group_config_payload_data,
#         'taxId': '9ba4975244574b519dc31aff6e0bb6e8',
#         'stock': 509,
#         'id': product_id,
#         'productNumber': product_number,
#         'price': [
#             {
#                 'currencyId': 'b7d2554b0ce847cd82f3ac9bd1c0dfca',
#                 'gross': price,
#                 'net': price / 1.19,
#                 'linked': True
#             }
#         ],
#         'name': name,
#         'properties': properties_payload_data,
#         'customFieldSets': [
#             {
#                 'name': 'additional_product_data',
#                 'id': md5('additional_product_data'.encode()).hexdigest(),
#                 'relations': [
#                     {
#                         'id': md5(f'customFieldSetsProductRelationsadditional_product_data'.encode()).hexdigest(),
#                         'entityName': "product"
#                     }
#                 ],
#                 'customFields': custom_field_sets_payload_data
#             },
#         ],
#         'customFields': custom_fields_payload_data,
#         'cmsPageId': '7a6d253a67204037966f42b0119704d5',
#         'visibilities': [
#             {
#                 'id': md5((product_number + 'visibility').encode()).hexdigest(),
#                 'salesChannelId': 'de020a57a3eb44d2b8f8070327b3d75b',
#                 'visibility': 30
#             }
#         ],
#         'ean': ean,
#         'deliveryTimeId': 'e497eddc39e4497f8a6c61afbd0bc294',
#         'manufacturerNumber': manufacturer_number,
#         'description': description + description_tail,
#         'manufacturer': {
#             'name': manufacturer_name,
#             'id': md5(manufacturer_name.encode()).hexdigest(),
#             'media': {
#                 'id': manufacturer_media_id,
#                 'mediaFolder':
#                     {
#                         'id': md5('API Manufacurer Media'.encode()).hexdigest(),
#                         'name': 'API Manufacurer Media',
#                         'configurationId': '381fbd435a594aafa817a9c207a77f9f',
#                     }
#             }
#         },
#         'media': product_image_payload_data,
#         'coverId': product_image_payload_data[0]['id'],
#         'categories': [product_category_payload_data],
#     }
#     payload = {
#         "create_product": {
#             "entity": "product",
#             "action": 'upsert',
#             'payload': [product_data]
#         }
#     }
#
#     # upload product
#     product_push = generate_admin_request('POST', f'https://{target}/api/_action/sync', target, username, password, payload)
#     product_resp_data = json.loads(product_push.text) if product_push.text != '' else 'no response => success'
#
#     # upload product images
#     all_images = set(image_urls + [image for child_data in data['children'] for image in child_data['images']])
#     for i, image_url in enumerate(all_images):
#         product_media_id = md5(image_url.encode()).hexdigest()
#         product_media_data = {'url': image_url}
#         fileextension = image_url.split('.')[-1]
#         product_media_push = generate_admin_request(
#             'POST', f'https://{target}/api/_action/media/{product_media_id}/upload?extension={fileextension}&fileName={product_number}_Produktbild_{i + 1}',
#             target, username, password, product_media_data)
#     print(f'images for product with number {product_number} (id={md5(product_number.encode()).hexdigest()}) uploaded')
#
#     # upload manufacturer and manufacturer image
#     manufacturor_media_data = {'url': manufacturer_image_url}
#     fileextension = manufacturer_image_url.split('.')[-1]
#     manufacturor_media_push = generate_admin_request(
#         'POST', f'https://{target}/api/_action/media/{manufacturer_media_id}/upload?extension={fileextension}&fileName={manufacturer_name}_Herstellerbild',
#         target, username, password, manufacturor_media_data)
#     manufacturor_resp_data = json.loads(manufacturor_media_push.text) if manufacturor_media_push.text != '' else 'no response => success'
#
#     return product_resp_data, manufacturor_resp_data
#
#
# def reduce_all_prices(target, username, password):
#     all_products = get_all_products(target, username, password,)
#     all_ids = [x['id'] for x in all_products]
#     datas = [
#         {
#             'id': uuid,
#             'visibilities': [
#                 {
#                     'id': md5((uuid + 'API Manufacurer Media').encode()).hexdigest(),
#                     'salesChannelId': 'de020a57a3eb44d2b8f8070327b3d75b',
#                     'visibility': 30
#                 }
#             ],
#             'deliveryTimeId': 'e497eddc39e4497f8a6c61afbd0bc294',
#
#         } for uuid in all_ids
#     ]
#
#     chunks = [
#         datas[x:x + 10] for x in range(0, len(datas), 10)
#     ]
#     for batch in chunks:
#         payload = {
#             "update_visibilities": {
#                 "entity": "product",
#                 "action": 'upsert',
#                 'payload': batch
#             }
#         }
#
#         product_push = generate_admin_request('POST', f'https://{target}/api/_action/sync', target, username, password, payload)
#
#
# def update_all_products(target, username, password):
#     all_products = get_all_products(target, username, password,)
#     all_ids = [x['id'] for x in all_products]
#     datas = [
#         {
#             'id': uuid,
#             'visibilities': [
#                 {
#                     'id': md5((uuid + 'API Manufacurer Media').encode()).hexdigest(),
#                     'salesChannelId': 'de020a57a3eb44d2b8f8070327b3d75b',
#                     'visibility': 30
#                 }
#             ],
#             'deliveryTimeId': 'e497eddc39e4497f8a6c61afbd0bc294',
#
#         } for uuid in all_ids
#     ]
#
#     chunks = [
#         datas[x:x + 10] for x in range(0, len(datas), 10)
#     ]
#     for batch in chunks:
#         payload = {
#             "update_visibilities": {
#                 "entity": "product",
#                 "action": 'upsert',
#                 'payload': batch
#             }
#         }
#
#         product_push = generate_admin_request('POST', f'https://{target}/api/_action/sync', target, username, password, payload)
#
#
# def upload_product_images(rootfolder, target, username, password):
#     all_product_images = set(open(f'{rootfolder}/cache/all_images.txt', 'r').read().splitlines())
#     all_image_urls_list = [
#         u for img_data in list(all_product_images) for image_urls in json.loads(img_data).values() for u in image_urls
#     ]
#     count = 0
#     tasks = []
#     with ThreadPoolExecutor(max_workers=10) as executor:
#
#         for img_data in list(all_product_images):
#             raw_line = img_data
#             img_data = json.loads(raw_line)
#             for product_number, image_urls in img_data.items():
#                 for i, image_url in enumerate(image_urls):
#                     if 'youtube' in image_url:
#                         continue
#                     count += 1
#                     product_media_id = md5(image_url.encode()).hexdigest()
#                     product_media_data_payload = {'url': image_url}
#                     fileextension = image_url.split('.')[-1]
#                     url = f'https://{target}/api/_action/media/{product_media_id}/upload?extension={fileextension}&fileName={product_number}_Produktbild_{i + 1}'
#                     tasks.append(executor.submit(generate_admin_request, 'POST', url, target, username, password, product_media_data_payload))
#
#                 for future in futures.as_completed(tasks):
#                     status = future.result().status_code
#                     print(future.result(), f'{count}/{len(all_image_urls_list)} uploaded')
#
#                 if status == 204:
#                     all_product_images.remove(raw_line)
#                     with open(f'{rootfolder}/cache/all_images.txt', 'w') as imagefile:
#                         [imagefile.write(line + '\n') for line in all_product_images]
#
#
# def edit_snippets(target, username, password, **data):
#
#     #  find out snippet-set Id
#
#     payload = {
#         'limit': 1,
#         'filter': [
#             {
#                 'type': 'equals',
#                 'field': 'name',
#                 'value': 'BASE de-DE',
#             }
#         ]
#     }
#
#     url = f'https://{target}/api/search/snippet-set'
#     response = generate_admin_request('POST', url, target, username, password, payload)
#     resp = response.json()
#     snippet_set_id = resp['data'][0]['id']
#
#     for name, value in data.items():
#         # find out snippet Id for footer.serviceHotline and others
#
#         payload = {
#             'limit': 10,
#             'filter': [
#                 {
#                     'type': 'equals',
#                     'field': 'translationKey',
#                     'value': name,
#                 },
#                 {
#                     'type': 'equals',
#                     'field': 'setId',
#                     'value': snippet_set_id,
#                 },
#             ]
#         }
#         url = f'https://{target}/api/search/snippet'
#         response = generate_admin_request('POST', url, target, username, password, payload)
#         resp = response.json()
#         snippet_id = resp['data'][0]['id']
#
#         # update snippet
#
#         payload = {'value': value}
#         url = f'https://{target}/api/snippet/{snippet_id}'
#         response = generate_admin_request('PATCH', url, target, username, password, payload)
#         resp = json.loads(response.text) if response.text != '' else 'no response => success'
#
#
# def edit_invoice_and_update_basic_config(target, username, password, data):
#
#     #  find out invoice id
#     payload = {
#         'limit': 1,
#         'filter': [
#             {
#                 'type': 'equals',
#                 'field': 'name',
#                 'value': 'invoice',
#             }
#         ]
#     }
#
#     url = f'https://{target}/api/search/document-base-config'
#     response = generate_admin_request('POST', url, target, username, password, payload)
#     resp = response.json()
#     document_id = resp['data'][0]['id']
#
#     tax_number = str(random.choice(range(20000, 22999)))
#     tax_number += str(random.choice(range(10000, 99999)))
#
#     invoice_config_payload = {
#             "config": {
#                 "companyName": data['imp_data']['company'],
#                 "taxNumber": tax_number,
#                 "vatId": data['imp_data']['ust_id'],
#                 "taxOffice": data['imp_data']['city'],
#                 "bankName": "BD BANK",
#                 "bankIban": "BD IBAN",
#                 "bankBic": "BD BIC",
#                 "placeOfJurisdiction": f"Deutschland <br /> Amtsgericht {data['imp_data']['city']}, {data['imp_data']['hrb'] } ",
#                 "placeOfFulfillment": data['imp_data']['city'],
#                 "executiveDirector": "BD Inhaber",
#                 "companyAddress": f"{data['imp_data']['address']}, {data['imp_data']['postcode']} {data['imp_data']['city']}",
#                 "companyUrl": f"www.{target}",
#                 "companyEmail": f"{data['imp_data']['prfx']}@{target}",
#                 "companyPhone": data['imp_data']['phone'],
#             }
#         }
#     url = f'https://{target}/api/document-base-config/{document_id}'
#     response = generate_admin_request('PATCH', url, target, username, password, invoice_config_payload)
#     resp = response.json()
#
#     ###
#
#     config_payload = {
#         None:
#             {
#                 'core.basicInformation.email': f"{data['imp_data']['prfx']}@{target}",
#                 'core.basicInformation.shopName': data['imp_data']['shop_name'],
#             }
#     }
#
#     url = f'https://{target}/api/_action/system-config/batch'
#     response = generate_admin_request('PATCH', url, target, username, password, config_payload)

if __name__ == '__main__':
    self = SW6Shop(
        target='example.com',
        username=None,
        password=None,
        upload_product_images=False,
    )
