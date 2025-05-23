"""
Module qui permet de se connecter de manière asynchrone à des serveur OPC UA.
Il permet de récupérer des informations sur des dispositifs à partir de
serveurs OPC UA,
de mettre à jour ou de créer des enregistrements dans Snipe-IT,
et de sauvegarder les résultats
dans un fichier JSON. Il inclut des fonctionnalités
pour gérer les modèles et les fabricants.
"""
import asyncio
import json
import argparse
import sys
import os
import logging
from asyncua import Client, ua
from asyncua.ua import NodeClass
import requests

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO")
'''
Partie Logging afin de mieux gérer mes erreurs quand je lance mon script
Permet de diagnostiquer l'éxecution du programme
'''

DATEFMT = "%FT%T%z"
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s",
    datefmt=DATEFMT,
)
RED = "\033[1;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[34m"
GREEN = "\033[1;32m"
RESET = "\033[1;0m"

logging.addLevelName(
    logging.ERROR, f"{RED}{logging.getLevelName(logging.ERROR)}{RESET}"
)
logging.addLevelName(
    logging.WARNING, f"{YELLOW}{logging.getLevelName(logging.WARNING)}{RESET}"
)
logging.addLevelName(
    logging.DEBUG, f"{BLUE}{logging.getLevelName(logging.DEBUG)}{RESET}"
)
logging.addLevelName(
    logging.INFO, f"{GREEN}{logging.getLevelName(logging.INFO)}{RESET}"
)

log = logging.getLogger(__name__)
log.setLevel(LOGLEVEL)

NAMESPACE_URI = "http://inno.merckgroup.com/sasi/"
BROWSE_PATH_DEFAUT = "Objects.DeviceId"
DESIRED_INFO = ["SerialNumber", "ModelId", "Vendor"]
url = "http://ec2-3-70-194-158.eu-central-1.compute.amazonaws.com:8000"
headers = {
    "Accept": "application/json",
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRp"
    "IjoiMTg2ZjIzY2NjODg4ZmZmMzNkODA3OGMxYzc0ZDFhZDhjMDBjM2Y1MGRmZjgxNDRmMjViODY1YTk0Y"
    "TdlYzQ0NjlkMDNlYzllNzg3ZTdiYjYiLCJpYXQiOjE3NDEwOTE2NzAuNzM4MTE5LCJuYmYiOjE3NDEwOT"
    "E2NzAuNzM4MTIyLCJleHAiOjMwMDMzOTU2NzAuNzM0NDIzLCJzdWIiOiIxIiwic2NvcGVzIjpbXX0.APj"
    "Zxb-ZZgDWMtjpm6kkExTz2Mer0pD0rpXu-wBDw_Cg6kisbXUF4Txt3gAAnhkbYC69JEZfBlH1_A3mkT1-"
    "U-MDJnMqMudRoDM1ZtZpK9NAWU1yVU3Zv9K4uT_nuhk-i5VUrabNtVQH-2Lkw8qipxqKxYKvDl4ViaR2F"
    "13x4VxGfhCKoRZjkliEeidzM740U_su_vB1DYecGteFGqDvbSg6SluVEmYO5VRsKJMqfaJPKLE3sXoOte"
    "0wrUwfIIdEyaPXfVlTz384VGK-G9bFTbGR4kqlw-A667HrOBp-TkkuUxNphPTPGPvxPoEit2hbapKvKnH"
    "1AM_pRRIHkHKhd-1SyJYMsRm8frZ9X7sLABCBxl3eMVN0BFBI4laF7DH30RnkL1HYRzoDnxudCTrO2y7i"
    "tN9kpcJlvvThGn6YZlgjDnxiJ2SZ_GGMUzyYIIBlZ3pA_Zj6OgTHQqxoZhrUxhnc2Pm-x1CsmJxo43i4O"
    "Zpm20qkjefWTztEtb8H5Aw0VYRPf47zARN6-NGOcOXSq4WOjcK2V1qA2QEhyM1qlMYEsInAEGAMZVc2O-"
    "oKQ_rYTN6bTkCjjbqYWDmmagt05n1BFDFY_r2iEo5jmA6rjT0s4FtJJSk858Nf6AO6hhP_BmTdclR-Ypv"
    "YYCnJpAtMLAHqUCCbwVKOx2dEChZXTR4",
    "Content-Type": "application/json"
}
'''
Variables globales
'''


class AsyncOpcUaFileClient:
    def __init__(self, endpoint_url):
        """
        Initialise le client OPC UA pour les opérations de fichier

        Args:
            endpoint_url: URL du serveur OPC UA (ex: "opc.tcp://localhost:4840")
        """
        self.endpoint_url = endpoint_url
        self.client = None

    async def connect(self):
        """Établit une connexion avec le serveur OPC UA"""
        try:
            self.client = Client(url=self.endpoint_url)
            await self.client.connect()
            log.info(f"Connecté au serveur OPC UA: {self.endpoint_url}")
            return True
        except Exception as ex:
            log.error(f"Erreur de connexion au serveur: {ex}")
            return False

    async def disconnect(self):
        """Déconnecte du serveur OPC UA"""
        if self.client:
            await self.client.disconnect()
            log.info("Déconnecté du serveur OPC UA")

    async def find_file_node(self, file_node_path):
        """
        Trouve un nœud de fichier sur le serveur OPC UA

        Args:
            file_node_path: Chemin du nœud (ex: "2:RawMTPfile")

        Returns:
            tuple: (node, methods_dict) où methods_dict contient les méthodes Open, Read, Close, etc.
        """
        try:
            path_parts = file_node_path.split("/")

            current_node = self.client.get_node("i=85")

            for part in path_parts:
                if ":" in part:
                    ns, name = part.split(":", 1)
                    ns = int(ns)
                else:
                    ns = 2
                    name = part

                children = await current_node.get_children()
                found = False

                for child in children:
                    browse_name = await child.read_browse_name()
                    if browse_name.Name == name and browse_name.NamespaceIndex == ns:
                        current_node = child
                        found = True
                        break

                if not found:
                    log.error(f"Nœud non trouvé: {part}")
                    return None, {}

            methods = {}
            children = await current_node.get_children()

            for child in children:
                node_class = await child.read_node_class()
                if node_class == NodeClass.Method:
                    browse_name = await child.read_browse_name()
                    methods[browse_name.Name] = child

            return current_node, methods

        except Exception as ex:
            log.error(f"Erreur lors de la recherche du nœud de fichier: {ex}")
            return None, {}

    async def open_file(self, file_node, methods, mode=1):
        """
        Ouvre un fichier sur le serveur OPC UA

        Args:
            file_node: Nœud du fichier
            methods: Dictionnaire des méthodes disponibles
            mode: Mode d'ouverture (1=lecture, 2=écriture)

        Returns:
            file_handle: Identifiant du fichier ouvert ou None en cas d'erreur
        """
        try:
            if "Open" not in methods:
                log.error("Méthode Open non trouvée")
                return None

            file_handle = await file_node.call_method(methods["Open"], mode)
            log.info(f"Fichier ouvert avec succès, handle: {file_handle}")
            return file_handle

        except Exception as ex:
            log.error(f"Erreur lors de l'ouverture du fichier: {ex}")
            return None

    async def read_file(self, file_node, methods, file_handle, size):
        """
        Lit des données depuis un fichier OPC UA

        Args:
            file_node: Nœud du fichier
            methods: Dictionnaire des méthodes disponibles
            file_handle: Identifiant du fichier ouvert
            size: Taille à lire

        Returns:
            bytes: Données lues ou None en cas d'erreur
        """
        try:
            if "Read" not in methods:
                log.error("Méthode Read non trouvée")
                return None

            data = await file_node.call_method(methods["Read"], file_handle, size)
            log.info(f"Lecture réussie: {len(data)} octets")
            return data

        except Exception as ex:
            log.error(f"Erreur lors de la lecture du fichier: {ex}")
            return None

    async def close_file(self, file_node, methods, file_handle):
        """
        Ferme un fichier OPC UA

        Args:
            file_node: Nœud du fichier
            methods: Dictionnaire des méthodes disponibles
            file_handle: Identifiant du fichier ouvert

        Returns:
            bool: True si la fermeture a réussi, False sinon
        """
        try:
            if "Close" not in methods:
                log.error("Méthode Close non trouvée")
                return False

            await file_node.call_method(methods["Close"], file_handle)
            log.info("Fichier fermé avec succès")
            return True

        except Exception as ex:
            log.error(f"Erreur lors de la fermeture du fichier: {ex}")
            return False

    async def download_file(self, file_node_path, output_path, chunk_size=4096):
        """
        Télécharge un fichier depuis le serveur OPC UA et l'enregistre localement

        Args:
            file_node_path: Chemin du nœud du fichier
            output_path: Chemin local où enregistrer le fichier
            chunk_size: Taille des blocs de lecture

        Returns:
            bool: True si le téléchargement a réussi, False sinon
        """
        try:
            file_node, methods = await self.find_file_node(file_node_path)
            if not file_node or not methods:
                return False

            required_methods = ["Open", "Read", "Close"]
            for method in required_methods:
                if method not in methods:
                    log.error(f"Méthode {method} non trouvée")
                    return False

            file_handle = await self.open_file(file_node, methods, mode=1)
            if not file_handle:
                return False

            try:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

                with open(output_path, 'wb') as f:
                    total_size = 0
                    while True:
                        data = await self.read_file(file_node, methods, file_handle, chunk_size)

                        if not data or len(data) == 0:
                            break

                        f.write(data)
                        total_size += len(data)

                log.info(f"Fichier téléchargé: {output_path} ({total_size} octets)")
                return True

            finally:
                await self.close_file(file_node, methods, file_handle)

        except Exception as ex:
            log.error(f"Erreur lors du téléchargement du fichier: {ex}")
            return False


async def download_mtp_file(server_url, file_node_path, output_path):
    """
    Télécharge un fichier MTP depuis un serveur OPC UA

    Args:
        server_url: URL du serveur OPC UA
        file_node_path: Chemin du nœud du fichier
        output_path: Chemin local où enregistrer le fichier

    Returns:
        bool: True si le téléchargement a réussi, False sinon
    """
    client = AsyncOpcUaFileClient(server_url)

    try:
        if await client.connect():
            download_success = await client.download_file(file_node_path, output_path)

            if download_success:
                log.info(f"Fichier MTP téléchargé avec succès: {output_path}")
                return True
            else:
                log.error("Échec du téléchargement du fichier MTP")
                return False
        else:
            log.error(f"Impossible de se connecter au serveur: {server_url}")
            return False
    except Exception as ex:
        log.error(f"Erreur lors du téléchargement du fichier MTP: {ex}")
        return False
    finally:
        await client.disconnect()


def upload_to_snipeit(file_path, api_url, asset_id, api_token):
    """
    Envoie un fichier à l'API Snipe-IT ou le met à jour s'il existe déjà

    Args:
        file_path: Chemin local du fichier à envoyer
        api_url: URL de base de l'API Snipe-IT (ex: "http://snipeit.example.com")
        asset_id: ID de l'asset auquel attacher le fichier
        api_token: Token d'authentification pour l'API

    Returns:
        dict: Réponse de l'API ou None en cas d'erreur
    """
    try:
        if not os.path.isfile(file_path):
            log.error(f"Le fichier n'existe pas: {file_path}")
            return None

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json"
        }

        # Récupérer la liste des fichiers existants pour cet asset
        files_endpoint = f"{api_url}/api/v1/hardware/{asset_id}/files"
        log.info(f"Vérification des fichiers existants pour l'asset {asset_id}")

        files_response = requests.get(files_endpoint, headers=headers)
        if files_response.status_code != 200:
            log.error(f"Impossible de récupérer la liste des fichiers: {files_response.status_code} - {files_response.text}")
            return None

        file_name = os.path.basename(file_path)
        existing_file_id = None

        try:
            files_data = files_response.json()
            if "rows" in files_data:
                for file_info in files_data["rows"]:
                    if file_info.get("filename") == file_name:
                        existing_file_id = file_info.get("id")
                        log.info(f"Fichier existant trouvé avec l'ID: {existing_file_id}")
                        break
        except Exception as ex:
            log.error(f"Erreur lors de l'analyse de la réponse JSON: {ex}")

        with open(file_path, 'rb') as f:
            files = {'file[]': (file_name, f, 'application/octet-stream')}

            if existing_file_id:
                delete_endpoint = f"{api_url}/api/v1/files/{existing_file_id}"
                log.info(f"Suppression du fichier existant avec l'ID {existing_file_id}")

                delete_response = requests.delete(delete_endpoint, headers=headers)
                if delete_response.status_code not in [200, 204]:
                    log.warning(f"Impossible de supprimer le fichier existant: {delete_response.status_code} - {delete_response.text}")

            upload_endpoint = f"{api_url}/api/v1/hardware/{asset_id}/files"
            log.info(f"Envoi du fichier {file_path} à {upload_endpoint}")

            response = requests.post(upload_endpoint, headers=headers, files=files)

            if response.status_code in [200, 201]:
                action = "mis à jour" if existing_file_id else "envoyé"
                log.info(f"Fichier {action} avec succès: {response.status_code}")
                return response.json()
            else:
                log.error(f"Erreur lors de l'envoi du fichier: {response.status_code} - {response.text}")
                return None

    except Exception as ex:
        log.error(f"Erreur lors de l'envoi du fichier à Snipe-IT: {ex}")
        return None


def find_asset_by_ip(api_url, api_token, ip_address):
    """
    Recherche un asset dans Snipe-IT par son adresse IP

    Args:
        api_url: URL de base de l'API Snipe-IT
        api_token: Token d'authentification pour l'API
        ip_address: Adresse IP à rechercher

    Returns:
        str: ID de l'asset trouvé ou None si aucun asset ne correspond
    """
    try:
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json"
        }

        search_endpoint = f"{api_url}/api/v1/hardware"
        params = {
            "search": ip_address,
            "limit": 50
        }

        log.info(f"Recherche d'un asset avec l'adresse IP: {ip_address}")
        response = requests.get(search_endpoint, headers=headers, params=params)

        if response.status_code != 200:
            log.error(f"Erreur lors de la recherche d'asset: {response.status_code} - {response.text}")
            return None

        try:
            assets_data = response.json()
            if "rows" in assets_data and len(assets_data["rows"]) > 0:
                for asset in assets_data["rows"]:
                    asset_name = asset.get("name", "").lower()
                    asset_serial = asset.get("serial", "").lower()
                    asset_asset_tag = asset.get("asset_tag", "").lower()
                    custom_fields = asset.get("custom_fields", {})
                    custom_field_values = []
                    for field in custom_fields.values():
                        if isinstance(field, dict) and "value" in field:
                            custom_field_values.append(str(field["value"]).lower())
                    if (ip_address.lower() in asset_name or
                        ip_address.lower() in asset_serial or
                        ip_address.lower() in asset_asset_tag or
                        any(ip_address.lower() in value for value in custom_field_values)):

                        asset_id = str(asset.get("id"))
                        log.info(f"Asset trouvé pour l'adresse IP {ip_address}: ID {asset_id}")
                        return asset_id

            log.warning(f"Aucun asset trouvé pour l'adresse IP: {ip_address}")
            return None

        except Exception as ex:
            log.error(f"Erreur lors de l'analyse de la réponse JSON: {ex}")
            return None

    except Exception as ex:
        log.error(f"Erreur lors de la recherche d'asset par IP: {ex}")
        return None


async def process_single_server(server_url, file_node_path, output_path, snipeit_config, location_id):
    """
    Traite un serveur OPC UA: télécharge le fichier MTP et l'envoie à Snipe-IT

    Args:
        server_url: URL du serveur OPC UA
        file_node_path: Chemin du nœud du fichier
        output_path: Chemin où enregistrer le fichier téléchargé
        snipeit_config: Configuration pour l'API Snipe-IT
        location_id: ID de la location dans Snipe-IT

    Returns:
        dict: Résultats des opérations ou None en cas d'erreur
    """
    results = {}

    try:
        ip_address = server_url.replace("opc.tcp://", "").split(":")[0]

        async with Client(url=server_url, timeout=10) as client:
            log.info(f'Connecté au serveur: {server_url}')
            device_info = await obtenir_info(client)
            log.info(f'Informations du device: {device_info}')
            snipeit_response = update_snipeit(
                device_info=device_info,
                headers=headers,
                server_ip=ip_address,
                location_id=location_id
            )

            results["device_info"] = device_info
            results["snipeit_response"] = snipeit_response

            asset_id = None
            if snipeit_response:
                if isinstance(snipeit_response, dict) and "payload" in snipeit_response and "id" in snipeit_response["payload"]:
                    asset_id = snipeit_response["payload"]["id"]
                elif isinstance(snipeit_response, dict) and "status" in snipeit_response and snipeit_response["status"] == "success":
                    # Chercher l'asset par son numéro de série
                    if "serialnumber" in device_info:
                        asset_id = find_asset_by_ip(
                            api_url=snipeit_config["url"],
                            api_token=snipeit_config["api_token"],
                            ip_address=ip_address
                        )

            if asset_id:
                file_client = AsyncOpcUaFileClient(server_url)
                if await file_client.connect():
                    download_success = await file_client.download_file(file_node_path, output_path)
                    await file_client.disconnect()

                    results["mtp_download"] = {
                        "success": download_success,
                        "path": output_path if download_success else None
                    }

                    if download_success:
                        upload_result = upload_to_snipeit(
                            file_path=output_path,
                            api_url=snipeit_config["url"],
                            asset_id=asset_id,
                            api_token=snipeit_config["api_token"]
                        )

                        results["mtp_upload"] = upload_result
                        return results
                    else:
                        results["error"] = "Échec du téléchargement du fichier MTP"
                        return results
                else:
                    results["error"] = "Impossible de se connecter au serveur pour télécharger le fichier MTP"
                    return results
            else:
                results["error"] = "Impossible de créer ou mettre à jour l'asset dans Snipe-IT"
                return results

    except Exception as ex:
        log.error(f"Erreur lors du traitement du serveur {server_url}: {ex}")
        return {"error": str(ex)}


async def process_multiple_servers(ip_addresses, file_node_path, output_dir, location_id, download_mtp=True):
    """
    Traite plusieurs serveurs OPC UA en séquence

    Args:
        ip_addresses: Liste des adresses IP des serveurs OPC UA
        file_node_path: Chemin du nœud du fichier sur chaque serveur
        output_dir: Répertoire où enregistrer les fichiers téléchargés
        location_id: ID de la location dans Snipe-IT
        download_mtp: Indique si les fichiers MTP doivent être téléchargés
    """

    if download_mtp:
        os.makedirs(output_dir, exist_ok=True)
    results = {}
    for ip in ip_addresses:
        log.info(f"Traitement du serveur: {ip}")
        server_url = f"opc.tcp://{ip}:4840"

        await browse_and_upgrade(
            results=results,
            server_url=server_url,
            location_id=location_id,
            download_mtp=download_mtp,
            mtp_node_path=file_node_path,
            output_dir=output_dir
        )

    log.info("=== Résumé des opérations ===")
    for server_url, result in results.items():
        ip = server_url.split("//")[1].split(":")[0]
        if "error" in result:
            log.info(f"Serveur {ip}: Échec - {result['error']}")
        else:
            mtp_status = "avec téléchargement MTP réussi" if result.get("mtp_download_success") else "sans téléchargement MTP"
            log.info(f"Serveur {ip}: Réussi {mtp_status}")

    return results


async def browse_and_upgrade_devices(server_urls, location_id):
    """"
    fonction principale qui se connecte au serveur OPC UA
    """
    results = {}
    for server_url in server_urls:
        await browse_and_upgrade(results, server_url, location_id)
    save_json(results)


async def browse_and_upgrade(results, server_url, location_id, download_mtp=False, mtp_node_path="2:RawMTPfile", output_dir="./mtp_files"):
    log.info('Trying to connect to server: %s', server_url)
    max_retries = 2
    ip_address = server_url.split("//")[1].split(":")[0]

    mtp_file_path = None
    if download_mtp:
        os.makedirs(output_dir, exist_ok=True)
        mtp_file_path = os.path.join(output_dir, f"{ip_address}_mtp_file.mtp")

    for attempt in range(max_retries):
        try:
            async with Client(url=server_url, timeout=10) as client:
                log.info('Connected to server: %s', server_url)
                device_info = await obtenir_info(client)
                log.info('Device Information: --> %s ', device_info)

                snipeit_response = update_snipeit(device_info, headers, ip_address, location_id)

                asset_id = None
                if isinstance(snipeit_response, dict):
                    if "payload" in snipeit_response and "id" in snipeit_response["payload"]:
                        asset_id = snipeit_response["payload"]["id"]
                    elif "status" in snipeit_response and snipeit_response["status"] == "success":
                        asset_tag = device_info.get('serialnumber', 'Unknown')
                        existing_asset = check_existing_asset(asset_tag)
                        if existing_asset:
                            asset_id = existing_asset["id"]
                mtp_download_success = False
                mtp_upload_response = None

                if download_mtp and asset_id and mtp_file_path:
                    log.info(f"Téléchargement du fichier MTP pour l'asset {asset_id}")
                    file_client = AsyncOpcUaFileClient(server_url)
                    if await file_client.connect():
                        try:
                            mtp_download_success = await file_client.download_file(mtp_node_path, mtp_file_path)

                            if mtp_download_success:
                                log.info(f"Fichier MTP téléchargé avec succès: {mtp_file_path}")
                                mtp_upload_response = upload_to_snipeit(
                                    file_path=mtp_file_path,
                                    api_url=url,
                                    asset_id=asset_id,
                                    api_token=headers["Authorization"].replace("Bearer ", "")
                                )

                                if mtp_upload_response:
                                    log.info(f"Fichier MTP envoyé à Snipe-IT pour l'asset {asset_id}")
                                else:
                                    log.error(f"Échec de l'envoi du fichier MTP à Snipe-IT pour l'asset {asset_id}")
                            else:
                                log.error("Échec du téléchargement du fichier MTP")
                        finally:
                            await file_client.disconnect()
                    else:
                        log.error(f"Impossible de se connecter au serveur pour télécharger le fichier MTP: {server_url}")

                results[server_url] = {
                    "device_info": device_info,
                    "snipeit_response": snipeit_response,
                    "mtp_download_success": mtp_download_success,
                    "mtp_file_path": mtp_file_path if mtp_download_success else None,
                    "mtp_upload_response": mtp_upload_response
                }
                break
        except asyncio.CancelledError:
            log.warning("Operation cancelled for server: %s", server_url)
            break
        except Exception as e:
            if attempt < max_retries - 1:
                log.info("Retrying connection...")
                await asyncio.sleep(0.1)
            else:
                results[server_url] = {"error": f"Max retries reached. Error: {str(e)}"}


async def translatebrowsepath(client, browse_path):
    """"
    Traduit le path en trouvant le noeud
    """
    try:
        path_parts = browse_path.split('.')
        node = client.get_root_node()
        for part in path_parts:
            children = await node.get_children()
            found = False
            for child in children:
                browse_name = (await child.read_browse_name()).Name
                if browse_name == part:
                    node = child
                    found = True
                    break
            if not found:
                raise Exception(f'Part of the path not found: {part}')
        return node
    except Exception as e:
        log.error('Error in translatebrowsepath : %s', e)
        return None


async def obtenir_info(client):
    device_info = {}
    try:
        device_id_node = await translatebrowsepath(client, BROWSE_PATH_DEFAUT)
        if device_id_node:
            children = await device_id_node.get_children()
            for child in children:
                name = (await child.read_browse_name()).Name
                if name in DESIRED_INFO:
                    log.info("Attempting to read value from node: %s", name)
                    value = await child.read_value()
                    log.info("Successfully read value: %s", value)
                    if isinstance(value, ua.LocalizedText):
                        value = value.Text
                    device_info[name.lower()] = str(value)
                    await asyncio.sleep(0.3)
    except asyncio.TimeoutError:
        log.error('Timeout error while obtaining device info.')
    except asyncio.CancelledError:
        log.warning('Operation cancelled while obtaining device info.')
    except Exception as e:
        log.error('Error in obtenir_info: %s', e)
    return device_info


def update_snipeit(device_info, headers, server_ip, location_id):
    """
    Met à jour Snipe-it en ajoutant ou en modifiant les infos d'un device
    Crée des model ou des manufacturers si nécessaire
    Ajoute ou met à jour la location pour les assets existants
    """
    model_id = get_or_create_model(device_info)
    manufacturer_id = get_or_create_manufacturer(device_info)
    log.info('Model_id is %s /// Manufacturer_id is %s', model_id, manufacturer_id)

    if (model_id is None or manufacturer_id is None
        or not isinstance(model_id, int)
            or not isinstance(manufacturer_id, int)):
        log.info("Cannot update Snipe-IT without valid model and manufacturer IDs.")
        return {"error": "Invalid model or manufacturer ID"}

    asset_tag = device_info.get('serialnumber', 'Unknown')
    existing_asset = check_existing_asset(asset_tag)

    if existing_asset:
        if not existing_asset.get('location') or existing_asset['location']['id'] != location_id:
            log.info(f"Updating location for existing asset {asset_tag}")
            return update_asset_location(existing_asset['id'], location_id)
        else:
            log.info(f"Asset {asset_tag} already exists with the correct location. No update needed.")
            return {"status": "success", "message": "Asset already exists with correct location"}

    payload = {
        "archived": False,
        "warranty_months": None,
        "depreciate": False,
        "supplier_id": None,
        "requestable": False,
        "rtd_location_id": None,
        "location_id": location_id,
        "asset_tag": asset_tag,
        "status_id": 2,
        "model_id": model_id,
        "serial": asset_tag,
        "name": device_info.get('modelid', 'Unknown Device'),
        "manufacturer_id": manufacturer_id,
        "category_id": 2,
        "_snipeit_ip_address_2": server_ip
    }

    log.info("Payload to Snipe-IT for new asset: %s", json.dumps(payload, indent=4))

    try:
        log.info("Attempting to create new hardware in Snipe-IT")
        response = requests.post(url + "/api/v1/hardware",
                                 json=payload, headers=headers, timeout=60)
        log.info("Response status code: %s", response.status_code)
        log.info("Response content: %s", response.content)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        log.error("Request to Snipe-IT timed out.")
        return {"error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        log.error("Error updating Snipe-IT: %s", e)
        return {"error": str(e)}


def get_or_create_model(device_info):
    """
    Vérifie si un model existe déjà dans Snipe-it / Si non, il le crée
    """
    model_id = search_model(device_info['modelid'])
    if model_id is not None:
        log.info('Model already exists with ID: %s', model_id)
        return model_id
    log.info('Creating new model ... ')
    manufacturer_id = get_or_create_manufacturer(device_info)
    if manufacturer_id is None:
        log.info("Cannot create model without a valid manufacturer.")
        return None
    model_id = create_model(device_info, manufacturer_id)
    if model_id is None:
        log.error("Failed to create model. Retrying with existing manufacturer...")
        model_id = create_model(device_info, manufacturer_id)
    return model_id


def search_model(model_name):
    """
    Recherche un model existant dans Snipe-it en fonction de son nom et retourne son ID
    """
    search_url = f'{url}/api/v1/models'
    response = requests.get(search_url, params={"name": model_name}, headers=headers,
                            timeout=60)
    if response.status_code != 200:
        log.error('Error fetching model: %s', response.content)
        response.raise_for_status()
    results = json.loads(response.content)
    if results.get('total', 0) == 0:
        log.info('Model not found')
        return None
    if 'rows' in results and len(results['rows']) > 0:
        return results['rows'][0]['id']
    log.error("Unexpected response format for models")
    return None


def create_model(device_info, manufacturer_id):
    """
    Crée un nouveau modèle s'il n'est pas trouvé par 'search_model'
    """
    create_url = f'{url}/api/v1/models'
    model_data = {
        "name": device_info['modelid'],
        "model_number": device_info['modelid'],
        "category_id": 2,
        "manufacturer_id": manufacturer_id,
        "requestable": True,
        "fieldset_id": 2
    }
    try:
        log.info("Attempting to create model: %s", device_info['modelid'])
        response = requests.post(create_url, json=model_data, headers=headers, timeout=60)
        log.info("Response status code: %s", response.status_code)
        log.info("Response content: %s", response.content)
        response.raise_for_status()
        created_model = response.json()
        if (created_model['status'] == 'success'
            and 'payload' in created_model
                and 'id' in created_model['payload']):
            log.info('New Model created with ID: %s', created_model["payload"]["id"])
            return created_model["payload"]["id"]
        log.error('Unexpected response format: %s', created_model)
        return None
    except requests.exceptions.RequestException as e:
        log.error('Error creating model: %s', e)
        return None


def get_or_create_manufacturer(device_info):
    """
    Vérifie si le manufacturer existe dans Snipe-it et le crée
    s'il n'existe pas en utilisant les infos du device
    """
    manufacturer_name = device_info.get('vendor')
    if manufacturer_name is None:
        log.info("Vendor information is missing in device_info.")
        return None
    manufacturer_id = search_manufacturer(manufacturer_name)
    if manufacturer_id is not None:
        log.info('Manufacturer already exists with ID: %s', manufacturer_id)
        return manufacturer_id
    log.info('Creating new manufacturer ... ')
    manufacturer_id = create_manufacturer(manufacturer_name)
    if manufacturer_id is None:
        log.error("Failed to create manufacturer.")
    return manufacturer_id


def search_manufacturer(manufacturer_name: str):
    """
    Recherche si le manufacturer existe déjà dans Snipe-it en fonction de son nom et retourne son ID
    """
    search_url = f'{url}/api/v1/manufacturers'
    response = requests.get(search_url,
                            params={"name": manufacturer_name}, headers=headers, timeout=60)
    if response.status_code != 200:
        log.error('Error: %s', response.content)
        response.raise_for_status()
    results = json.loads(response.content)
    if results.get('total', 0) == 0:
        log.info('Manufacturer not found')
        return None
    if 'rows' in results and len(results['rows']) > 0:
        return results['rows'][0]['id']
    log.error("Unexpected response format for manufacturers")
    return None


def create_manufacturer(manufacturer_name):
    """
    Crée un nouveau manufacturer s'il n'existe pas
    """
    create_url = f'{url}/api/v1/manufacturers'
    manufacturer_data = {
        "name": manufacturer_name,
        "archived": False,
        "warranty_months": None,
        "requestable": False,
        "category_id": 2
    }
    try:
        log.info("Attempting to create manufacturer: %s", manufacturer_name)
        response = requests.post(create_url, json=manufacturer_data,
                                 headers=headers, timeout=60)
        log.info("Response status code: %s", response.status_code)
        log.info("Response content: %s", response.content)
        response.raise_for_status()
        created_manufacturer = response.json()
        if (created_manufacturer['status'] == 'success' and
            'payload' in created_manufacturer and
                'id' in created_manufacturer['payload']):

            log.info('New Manufacturer created with ID: %s', created_manufacturer["payload"]["id"])
            return created_manufacturer["payload"]["id"]
        log.error('Unexpected response format: %s', created_manufacturer)
        return None
    except requests.exceptions.RequestException as e:
        log.error('Error creating manufacturer: %s', e)
        return None


def check_existing_asset(asset_tag):
    """
    Vérifie si un asset existe déjà dans Snipe-IT
    """
    search_url = f'{url}/api/v1/hardware'
    try:
        response = requests.get(search_url, params={"asset_tag": asset_tag}, headers=headers, timeout=60)
        response.raise_for_status()
        results = response.json()
        if results.get('total', 0) > 0 and 'rows' in results and len(results['rows']) > 0:
            return results['rows'][0]
        return None
    except requests.exceptions.RequestException as e:
        log.error(f'Error checking existing asset: {e}')
        return None


def get_location_id(location_name):
    """
    Obtient l'ID de la location à partir de son nom dans Snipe-IT
    """
    search_url = f'{url}/api/v1/locations'
    try:
        response = requests.get(search_url, params={"search": location_name}, headers=headers, timeout=60)
        response.raise_for_status()
        results = response.json()
        if results.get('total', 0) > 0 and 'rows' in results and len(results['rows']) > 0:
            return results['rows'][0]['id']
        log.warning(f"Location '{location_name}' not found in Snipe-IT")
        return None
    except requests.exceptions.RequestException as e:
        log.error(f'Error searching for location: {e}')
        return None


def get_assets_by_location(location_id):
    """
    Récupère tous les assets pour une location donnée dans Snipe-IT
    """
    search_url = f'{url}/api/v1/hardware'
    try:
        response = requests.get(search_url, params={"location_id": location_id}, headers=headers, timeout=60)
        response.raise_for_status()
        results = response.json()
        if results.get('total', 0) > 0 and 'rows' in results:
            return results['rows']
        return []
    except requests.exceptions.RequestException as e:
        log.error(f'Error fetching assets for location: {e}')
        return []


def update_asset_location(asset_id, location_id):
    """
    Met à jour la location d'un asset existant dans Snipe-IT
    """
    update_url = f'{url}/api/v1/hardware/{asset_id}'
    payload = {
        "location_id": location_id
    }
    try:
        log.info(f"Updating location for asset ID {asset_id} to location ID {location_id}")
        response = requests.patch(update_url, json=payload, headers=headers, timeout=60)
        log.info("Response status code: %s", response.status_code)
        log.info("Response content: %s", response.content)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log.error(f"Error updating asset location: {e}")
        return {"error": str(e)}


def remove_asset_location(asset_id):
    """
    Supprime la location_id d'un asset dans Snipe-IT
    """
    update_url = f'{url}/api/v1/hardware/{asset_id}'
    payload = {
        "location_id": None
    }
    try:
        log.info(f"Removing location for asset ID {asset_id}")
        response = requests.patch(update_url, json=payload, headers=headers, timeout=60)
        log.info("Response status code: %s", response.status_code)
        log.info("Response content: %s", response.content)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log.error(f"Error removing asset location: {e}")
        return {"error": str(e)}


def save_json(data):
    """
    Sauvegarde les données collectés dans un fichier JSON pour les utiliser par la suite
    """
    filename = 'data.json'

    def default(obj):
        return str(obj)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False, default=default)


async def main():
    """
    Fonction principale qui gère les arguments de ligne de commande
    Récupère les @IP des serveurs OPC UA
    Appelle les fonctions appropriées pour traiter les infos du device
    et télécharger les fichiers MTP si demandé
    """
    parser = argparse.ArgumentParser(description="Client OPC UA et intégration Snipe-IT")
    parser.add_argument("--server", help='Endpoint du serveur OPC UA', required=False)
    parser.add_argument("--list", help='Liste des adresses IP des serveurs OPC UA (une par ligne)',
                        action="store_true", default=False, required=False)
    parser.add_argument("--location", help="Location de l'asset dans l'Innovation Space", required=True)

    mtp_group = parser.add_mutually_exclusive_group()
    mtp_group.add_argument("--download-mtp", help="Télécharger les fichiers MTP depuis les serveurs OPC UA",
                      action="store_true", default=False)
    mtp_group.add_argument("--no-mtp", help="Ne pas télécharger les fichiers MTP (utile pour cron)",
                      action="store_true", default=False)

    parser.add_argument("--mtp-path", help="Chemin du nœud du fichier MTP (ex: '2:RawMTPfile')",
                        default="2:RawMTPfile")
    parser.add_argument("--output-dir", help="Répertoire où enregistrer les fichiers MTP téléchargés",
                        default="./mtp_files")
    parser.add_argument("--check-missing", help="Vérifier et supprimer la location des assets qui ne sont plus présents",
                        action="store_true", default=False)

    args = parser.parse_args()

    if not args.server and not args.list or not args.location:
        log.error("Erreur : Fournir l'un des arguments suivants :")
        log.error("  --server <adresse> : Pour spécifier un seul serveur OPC UA.")
        log.error("  --list : Pour utiliser une liste d'adresses IP des "
                    "serveurs OPC UA (une par ligne).")
        log.error("  --location : Pour spécifier sur quel Bench se trouve l'asset.")
        sys.exit(1)

    location_id = get_location_id(args.location)
    if location_id is None:
        log.error(f"La location '{args.location}' n'a pas été trouvée dans Snipe-IT. Veuillez vérifier le nom et réessayer.")
        sys.exit(1)

    download_mtp = args.download_mtp and not args.no_mtp

    if download_mtp:
        os.makedirs(args.output_dir, exist_ok=True)
        log.info(f"Les fichiers MTP seront téléchargés dans le répertoire: {args.output_dir}")
        log.info(f"Chemin du nœud MTP: {args.mtp_path}")
    else:
        if args.no_mtp:
            log.info("Téléchargement des fichiers MTP désactivé (--no-mtp)")
        else:
            log.info("Téléchargement des fichiers MTP non demandé")

    results = {}
    if args.list:
        log.info("Entrez les adresses IP des serveurs OPC UA (terminez par une ligne vide):")
        ip_addresses = []
        while True:
            try:
                ip = input("Adresse IP: ").strip()
                if not ip:
                    break
                ip_addresses.append(ip)
            except EOFError:
                break

        if ip_addresses:
            log.info(f"Traitement de {len(ip_addresses)} serveurs: {', '.join(ip_addresses)}")
            results = await process_multiple_servers(
                ip_addresses=ip_addresses,
                file_node_path=args.mtp_path,
                output_dir=args.output_dir,
                location_id=location_id,
                download_mtp=download_mtp
            )
        else:
            log.warning("Aucune adresse IP fournie.")
    else:
        server_url = args.server
        if server_url.startswith("opc.tcp://"):
            ip = server_url.replace("opc.tcp://", "").split(":")[0]
        else:
            ip = server_url
            server_url = f"opc.tcp://{ip}:4840"
        results = await process_multiple_servers(
            ip_addresses=[ip],
            file_node_path=args.mtp_path,
            output_dir=args.output_dir,
            location_id=location_id,
            download_mtp=download_mtp
        )

    if args.check_missing:
        existing_assets = get_assets_by_location(location_id)
        discovered_serials = set()

        for server_url, server_data in results.items():
            if isinstance(server_data, dict) and "device_info" in server_data:
                device_info = server_data["device_info"]
                if isinstance(device_info, dict) and "serialnumber" in device_info:
                    serial = device_info["serialnumber"]
                    log.info(f"Asset découvert: {serial} sur {server_url}")
                    discovered_serials.add(serial)

        log.info(f"Numéros de série découverts: {discovered_serials}")
        log.info(f"Nombre d'assets existants dans la location: {len(existing_assets)}")

        if discovered_serials:
            for asset in existing_assets:
                if asset.get('serial') and asset['serial'] not in discovered_serials:
                    log.info(f"Asset {asset['serial']} n'est plus présent dans la location. Suppression de la location.")
                    remove_asset_location(asset['id'])
        else:
            log.warning("Aucun numéro de série découvert. Vérification des assets existants ignorée.")
    else:
        log.info("Vérification des assets manquants désactivée.")

    save_json(results)
    log.info("Résultats sauvegardés dans data.json")
    log.info(f"Mise à jour des assets dans Snipe-IT terminée: {url}")

if __name__ == "__main__":
    asyncio.run(main())
