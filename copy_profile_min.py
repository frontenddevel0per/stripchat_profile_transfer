from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium.webdriver.common.keys import Keys
import requests
import os
import shutil
from pynput.keyboard import Key, Controller
import re
from pprint import pprint
from seleniumbase import Driver
import concurrent.futures
import traceback


def split_array(array):
    if len(array) == 0:
        return []

    chunks = [array[i : i + 23] for i in range(1, len(array), 23)]

    chunks.insert(0, [array[0]])

    return chunks


def upload_content(url, path, type, data, cookies_dict):
    with open(path, "rb") as file:
        files = {type: file}
        requests.post(
            url,
            files=files,
            data=data,
            cookies=cookies_dict,
        )

def upload_video(video, path, modelId, cookies_dict, csrfNotify, csrfTimestamp, csrfToken):
    video_size = os.path.getsize(path)
    ans1 = requests.post(f"https://mywebcamroom.com/api/front/users/{modelId}/videos/upload-url", data={
        "csrfNotifyTimestamp": csrfNotify,
        "csrfTimestamp": csrfTimestamp,
        "csrfToken": csrfToken,
        "filename": path.split("\\")[-1],
        "filesize": video_size
    },
    cookies=cookies_dict).json()
    with open(path, "rb") as videoFile:
        files = {"file": videoFile}
        ans2 = requests.post(
            ans1["url"],
            files=files,
            data={
                "csrfNotifyTimestamp": csrfNotify,
                "csrfTimestamp": csrfTimestamp,
                "csrfToken": csrfToken
            },
            cookies=cookies_dict,
        ).json()
    try:
        ans3 = requests.post(f"https://mywebcamroom.com/api/front/v2/users/{modelId}/videos",headers={"content-type": "application/json"}, json={
            "title": path.split("\\")[-1],
            "accessMode": "free",
            "coverUrls": [],
            "cost": 0,
            "csrfNotifyTimestamp": csrfNotify,
            "csrfTimestamp": csrfTimestamp,
            "csrfToken": csrfToken,
            "details": {},
            "uploadId": ans2["uploadId"]
        },
        cookies=cookies_dict).json()
        new_video = dict(ans3["video"])
        new_video["title"] = video["title"]
        new_video["accessMode"] = (
            video["accessMode"]
            if video["accessMode"] != "fanClub"
            else "paidOrFanClub"
        )
        new_video["cost"] = video["cost"]
        new_video["minFanClubTier"] = video["minFanClubTier"]
        new_video["csrfNotifyTimestamp"] = csrfNotify
        new_video["csrfTimestamp"] = csrfTimestamp
        new_video["csrfToken"] = csrfToken
        requests.put(f"https://mywebcamroom.com/api/front/v2/users/{modelId}/videos/{new_video["id"]}",json=new_video,cookies=cookies_dict)
    except:
        traceback.print_exc()

def upload_panel(path, modelId, data, cookies_dict):
    if path != "":
        with open(path, "rb") as photo:
            files = {"image": photo}
            requests.post(f"https://mywebcamroom.com/api/front/users/{modelId}/panels", files=files, data=data, cookies=cookies_dict).json()
    else:
        requests.post(f"https://mywebcamroom.com/api/front/users/{modelId}/panels", data=data, cookies=cookies_dict).json()

class ProfileTransfer:
    def __init__(self):
        requested_dirs = ["videos", "photos", "panels", "profile"]

        self.script_location = os.path.dirname(os.path.realpath(__file__))

        for dir in requested_dirs:
            if os.path.exists(f"{self.script_location}\\{dir}"):
                shutil.rmtree(f"{self.script_location}\\{dir}")
            os.makedirs(f"{self.script_location}\\{dir}")

        self.keyboard = Controller()

        self.model_profile = {
            "my_information": {},
            "background": False,
            "panels": [],
            "videos": [],
            "photos": [],
            "broadcast_settings": {
                "show_activities": {},
                "pricing": {},
                "record": {},
                "tip_menu": {},
                "extensions": [],
                "teaser": False,
            },
        }

    def download_video(self, url, file_name):
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(file_name, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

    def wait_for_page_load(self, driver):
        WebDriverWait(driver, 10).until(
            lambda x: x.execute_script("return document.readyState === 'complete'")
        )

    def scroll_to_elem(self, driver, elem):
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center',behaviour: 'instant'});", elem
        )

    def click_element(self, driver, selector):
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(("css selector", selector))
        )
        self.scroll_to_elem(driver, element)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(element))
        element.click()

    def login_stripchat(self, driver, login, password):
        driver.get("https://mywebcamroom.com")
        self.wait_for_page_load(driver)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(("css selector", "#login_login_or_email"))
        )
        driver.find_element("css selector", "#login_login_or_email").send_keys(login)
        driver.find_element("css selector", "#login_password").send_keys(password)
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located(("css selector", "span.avatar"))
        )

    def clear_input(self, driver, element):
        self.scroll_to_elem(driver, element)
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable(element))
        element.click()
        element.send_keys(Keys.CONTROL + "a")  # Select all existing text
        element.send_keys(Keys.DELETE)
        sleep(0.1)

    def download_all_videos(self, driver: Chrome, login):
        executor = concurrent.futures.ThreadPoolExecutor()
        tasks = []
        videos = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/v2/users/username/'
            + login
            + '/videos?uniq=",{mode:"cors",credentials:"include"}).then(e=>e.json()).then(e=>e.videos);'
        )
        for video in videos:
            if "Private Show" in video["title"]:
                continue
            self.model_profile["videos"].append(video)
            tasks.append(
                executor.submit(
                    self.download_video,
                    url = video["videoUrl"],
                    file_name = f"{self.script_location}\\videos\\{video['id']}.mp4"
                )
            )
        concurrent.futures.wait(tasks)

    def download_all_photos(self, driver: Chrome, login: str):
        albums = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/v2/users/username/'
            + login
            + '/albums?limit=50&offset=0&uniq=",{mode:"cors",credentials:"include"}).then(e=>e.json()).then(e=>e.albums);'
        )
        self.model_profile["photos"] = albums
        for album in albums:
            album_name = re.sub(r"[^\w_. -]", "_", album["name"])
            os.makedirs(f"{self.script_location}\\photos\\{album_name}")
            for photo in album["photos"]:
                response = requests.get(photo["url"])
                with open(
                    f"{self.script_location}\\photos\\{album_name}\\{photo['id']}.jpg",
                    "wb",
                ) as f:
                    f.write(response.content)

    def copy_broadcast_settings(self, driver: Chrome, id):
        data = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/v2/config?uniq=",{mode:"cors",credentials:"include"}).then(n=>n.json()).then(n=>n.data);'
        )
        self.model_profile["broadcast_settings"]["show_activities"] = {
            "publicActivities": data["user"]["publicActivities"],
            "privateActivities": data["user"]["privateActivities"],
            "exclusivePrivateActivities": data["user"]["exclusivePrivateActivities"],
        }
        self.model_profile["broadcast_settings"]["offlineStatus"] = data["user"][
            "offlineStatus"
        ]
        response = requests.get(data["user"]["sourcePreviewUrl"])
        with open(f"{self.script_location}\\profile\\cover_image.jpg", "wb") as f:
            f.write(response.content)
        self.model_profile["broadcast_settings"]["pricing"] = {
            "privateRate": data["user"]["privateRate"],
            "privateMinDuration": data["user"]["privateMinDuration"],
            "p2pRate": data["user"]["p2pRate"],
            "p2pMinDuration": data["user"]["p2pMinDuration"],
            "spyRate": data["user"]["spyRate"],
            "groupRate": data["user"]["groupRate"],
            "ticketRate": data["user"]["ticketRate"],
            "p2pVoiceRate": data["user"]["p2pVoiceRate"],
        }
        self.model_profile["broadcast_settings"]["record"] = {
            "isStorePublicRecordings": data["user"]["isStorePublicRecordings"],
            "isStorePrivateRecordings": data["user"]["isStorePrivateRecordings"],
            "publicRecordingsRate": data["user"]["publicRecordingsRate"],
        }
        self.model_profile["broadcast_settings"]["becomeKingThreshold"] = data["user"][
            "becomeKingThreshold"
        ]
        tipMenuData = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/models/'
            + str(id)
            + '/tip/menu?uniq=",{mode:"cors",credentials:"include"}).then(e=>e.json()).then(e=>e.tipMenu);'
        )
        self.model_profile["broadcast_settings"]["tip_menu"] = {
            "isEnabled": tipMenuData["isEnabled"],
            "presets": tipMenuData["presets"],
        }

    def download_teaser_video(self, driver: Chrome, id):
        teaserUrl = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/users/'
            + str(id)
            + '?uniq=",{mode:"cors",credentials:"include"}).then(e=>e.json()).then(e=>e?.teaser?.url);'
        )
        if teaserUrl:
            self.model_profile["broadcast_settings"]["teaser"] = True
            self.download_video(
                teaserUrl, f"{self.script_location}\\videos\\teaser.mp4"
            )

    def copy_extensions(self, driver: Chrome, id):
        extensionsData = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/users/'
            + str(id)
            + '/apps?status=approved&uniq=",{mode:"cors",credentials:"include"}).then(s=>s.json()).then(s=>s.apps);'
        )
        print(extensionsData)
        self.model_profile["broadcast_settings"]["extensions"] = extensionsData

    def copy_my_info(self, driver: Chrome, id):
        data = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/v2/config?uniq=",{mode:"cors",credentials:"include"}).then(n=>n.json()).then(n=>n.data);'
        )
        self.model_profile["my_information"] = {
            key: data["user"][key]
            for key in [
                "name",
                "birthDate",
                "interestedIn",
                "languages",
                "bodyType",
                "specifics",
                "ethnicity",
                "hairColor",
                "eyeColor",
                "subculture",
                "interests",
            ]
        }
        response = requests.get(data["user"]["avatarUrl"])
        with open(f"{self.script_location}\\profile\\avatar.jpg", "wb") as f:
            f.write(response.content)
        background = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/users/'
            + str(id)
            + '/intros/latest?uniq=",{mode:"cors",credentials:"include"}).then(e=>e.json());'
        )
        if background != []:
            self.model_profile["background"] = background["type"]
            if background["type"] == "image":
                response = requests.get(background["image"]["url"])
                with open(
                    f"{self.script_location}\\profile\\background.jpg", "wb"
                ) as f:
                    f.write(response.content)
            else:
                self.download_video(
                    background["video"]["url"],
                    f"{self.script_location}\\profile\\background.mp4",
                )
        self.model_profile["panels"] = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/users/'
            + str(id)
            + '/panels?uniq=",{mode:"cors",credentials:"include"}).then(e=>e.json()).then(p=>p.panels);'
        )
        for panel in self.model_profile["panels"]:
            response = requests.get(panel["imageUrl"])
            with open(f"{self.script_location}\\panels\\{panel['id']}.jpg", "wb") as f:
                f.write(response.content)

    def change_my_info(self, driver: Chrome, id, csrfNotify, csrfTimestamp, csrfToken):
        driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/users/'
            + str(id)
            + '",{headers:{"content-type":"application/json"},body:JSON.stringify(arguments[0]),method:"POST",mode:"cors",credentials:"include"});',
            dict(
                list(self.model_profile["my_information"].items())
                + list(
                    {
                        "csrfNotifyTimestamp": csrfNotify,
                        "csrfTimestamp": csrfTimestamp,
                        "csrfToken": csrfToken,
                    }.items()
                )
            ),
        )

        """self.click_element(driver, "#user_info_editable_edit_button")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(("css selector", ".details-edit-mode"))
        )

        fields = driver.find_elements("css selector", "div[id*='user_info_editable']")
        for field in fields:
            self.scroll_to_elem(driver, field)
            field_id = field.get_attribute("id").replace("user_info_editable_", "")
            if field_id == "gender":
                continue
            field_value = self.model_profile["my_information"][field_id]
            try:
                field_input = field.find_element("css selector", "input")
                if field_input.get_attribute("type") == "date":
                    driver.execute_script(
                        f"document.querySelector('#user_info_editable_displayedBirthDate > div.input-date-wrapper > input').value = '{field_value}'"
                    )
                else:
                    field_input.clear()
                    field_input.send_keys(field_value)
            except:
                if field_id != "interests":
                    if field_id == "languages" or field_id == "specifics":
                        while True:
                            try:
                                field.find_element(
                                    "css selector", ".select-value-icon"
                                ).click()
                                sleep(0.1)
                            except:
                                break
                        field.click()
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                ("css selector", ".select-menu-outer")
                            )
                        )
                        for value in field_value:
                            for option in driver.find_elements(
                                "css selector", ".select-menu-outer div[data-value]"
                            ):
                                if option.get_attribute("innerText") == value:
                                    self.scroll_to_elem(driver, option)
                                    WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable(option)
                                    )
                                    option.click()
                                    sleep(0.25)
                                    break
                        field.click()
                    else:
                        field.click()
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                ("css selector", ".select-menu-outer")
                            )
                        )
                        required_value = list(
                            filter(
                                lambda x: x.get_attribute("innerText") == field_value,
                                field.find_elements(
                                    "css selector", ".select-menu-outer div[data-value]"
                                ),
                            )
                        )[0]
                        self.scroll_to_elem(driver, required_value)
                        required_value.click()
                else:
                    while True:
                        try:
                            driver.find_element(
                                "css selector", ".interest-item__remove-button"
                            ).click()
                            sleep(0.1)
                        except:
                            break
                    driver.find_element(
                        "css selector", ".user-info-editable__choose-interests"
                    ).click()
                    interests_content = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            ("css selector", ".interests-modal__content")
                        )
                    )
                    see_more_btns = interests_content.find_elements(
                        "css selector", ".see-more-button"
                    )
                    for btn in see_more_btns:
                        self.scroll_to_elem(driver, btn)
                        btn.click()
                    for value in field_value:
                        interest = interests_content.find_element(
                            "css selector", f"#{value}"
                        )
                        self.scroll_to_elem(driver, interest)
                        interest.click()
                    driver.find_element(
                        "css selector", ".interests-modal__save-button"
                    ).click()
        save_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                ("css selector", "#user_info_editable_edit_button > button")
            )
        )
        self.scroll_to_elem(driver, save_btn)
        save_btn.click()"""

    def add_panels(
        self, driver: Chrome, login, id, csrfNotify, csrfTimestamp, csrfToken
    ):
        panels = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/users/'
            + str(id)
            + '/panels?uniq=",{mode:"cors",credentials:"include"}).then(e=>e.json()).then(p=>p.panels);'
        )
        for panel in panels:
            driver.execute_script(
                'await fetch("https://mywebcamroom.com/api/front/users/'
                + str(id)
                + "/panels/"
                + str(panel["id"])
                + '",{headers:{"content-type":"application/json"},body:JSON.stringify(arguments[0]),method:"DELETE",mode:"cors",credentials:"include"});',
                {
                    "csrfNotifyTimestamp": csrfNotify,
                    "csrfTimestamp": csrfTimestamp,
                    "csrfToken": csrfToken,
                },
            )
        executor = concurrent.futures.ThreadPoolExecutor()
        tasks = []
        cookies = driver.get_cookies()
        cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
        for panel in self.model_profile["panels"]:
            data = {
                "title": panel["title"],
                "body": panel["body"],
                "position[column]": panel["position"]["column"],
                "position[order]": panel["position"]["order"],
                "csrfNotifyTimestamp": csrfNotify,
                "csrfTimestamp": csrfTimestamp,
                "csrfToken": csrfToken,
            }
            tasks.append(
                executor.submit(
                    upload_panel,
                    path="" if panel["imageUrl"] == "" else f"{self.script_location}\\panels\\{panel['id']}.jpg",
                    modelId = id,
                    data=data,
                    cookies_dict=cookies_dict
                )
            )
        concurrent.futures.wait(tasks)
        '''panels = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/users/'
            + str(id)
            + '/panels?uniq=",{mode:"cors",credentials:"include"}).then(e=>e.json()).then(p=>p.panels);'
        )
        for panel in panels:
            driver.execute_script(
                'await fetch("https://mywebcamroom.com/api/front/users/'
                + str(id)
                + "/panels/"
                + str(panel["id"])
                + '",{headers:{"content-type":"application/json"},body:JSON.stringify(arguments[0]),method:"DELETE",mode:"cors",credentials:"include"});',
                {
                    "csrfNotifyTimestamp": csrfNotify,
                    "csrfTimestamp": csrfTimestamp,
                    "csrfToken": csrfToken,
                },
            )
        driver.get(f"https://mywebcamroom.com/{login}/profile")
        addPanelBtn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                ("css selector", "button.profile-panel-add-btn")
            )
        )
        self.scroll_to_elem(driver, addPanelBtn)
        for panel in self.model_profile["panels"]:
            addPanelBtn.click()
            sleep(1)
            titleTextarea = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    ("css selector", 'textarea[id="panel_title_textarea_id"]')
                )
            )
            panel["title"] != "" and titleTextarea.send_keys(panel["title"])
            panel["body"] != "" and driver.find_element(
                "css selector", 'textarea[id="panel_body_textarea_id"]'
            ).send_keys(panel["body"])
            if panel["imageUrl"] != "":
                driver.find_element(
                    "css selector", 'button[id="panel_image_file_input_id"]'
                ).click()
                sleep(2)
                self.keyboard.type(f"{self.script_location}\\panels\\{panel['id']}.jpg")
                self.keyboard.press(Key.enter)
                self.keyboard.release(Key.enter)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        ("css selector", "div.panel-image-preview-small img")
                    )
                )
            driver.execute_script(
                "document.querySelector('.modal-body button[type=\"submit\"]').click()"
            )
            sleep(1)'''

    def upload_background(self, driver: Chrome, login, id):
        if self.model_profile["background"] == False:
            return
        background = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/users/'
            + str(id)
            + '/intros/latest?uniq=",{mode:"cors",credentials:"include"}).then(e=>e.json());'
        )
        mode = (
            "Upload"
            if background == []
            or background["type"] != self.model_profile["background"]
            else "Update"
        )
        driver.get(f"https://mywebcamroom.com/{login}/profile")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                ("css selector", "button.profile-cover-dropdown__button")
            )
        ).click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                ("css selector", "button.profile-cover-dropdown__action")
            )
        )
        sleep(1)
        list(
            filter(
                lambda button: button.get_attribute("innerText")
                == f"{mode} {'Image' if self.model_profile['background'] == 'image' else 'Video'}",
                driver.find_elements("css selector", ".profile-cover-dropdown__action"),
            )
        )[0].click()
        sleep(2)
        self.keyboard.type(
            f"{self.script_location}\\profile\\background.{'jpg' if self.model_profile['background'] == 'image' else 'mp4'}"
        )
        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter)
        for i in range(30):
            if background != driver.execute_script(
                'return await fetch("https://mywebcamroom.com/api/front/users/'
                + str(id)
                + '/intros/latest?uniq=",{mode:"cors",credentials:"include"}).then(e=>e.json());'
            ):
                break
            sleep(1)

    def upload_all_photos(
        self, driver: Chrome, login, id, csrfNotify, csrfTimestamp, csrfToken
    ):
        for album in self.model_profile["photos"]:
            if album["name"] != "Public":
                ans = driver.execute_script(
                    'return await fetch("https://mywebcamroom.com/api/front/v2/users/'
                    + str(id)
                    + '/albums",{headers:{"content-type":"application/json"},body:JSON.stringify(arguments[0]),method:"POST",mode:"cors",credentials:"include"}).then(r=>r.json());',
                    {
                        "accessMode": album["accessMode"],
                        "cost": album["cost"],
                        "minFanClubTier": album["minFanClubTier"],
                        "name": album["name"],
                        "csrfNotifyTimestamp": csrfNotify,
                        "csrfTimestamp": csrfTimestamp,
                        "csrfToken": csrfToken,
                    },
                )
                print(ans)
        new_albums = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/v2/users/username/'
            + login
            + '/albums?limit=50&offset=0&uniq=",{mode:"cors",credentials:"include"}).then(e=>e.json()).then(e=>e.albums);'
        )
        executor = concurrent.futures.ThreadPoolExecutor()
        tasks = []
        cookies = driver.get_cookies()
        cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
        data = {
            "source": "albums",
            "csrfNotifyTimestamp": csrfNotify,
            "csrfTimestamp": csrfTimestamp,
            "csrfToken": csrfToken,
        }
        for album in self.model_profile["photos"]:
            searched_album = list(
                filter(lambda x: x["name"] == album["name"], new_albums)
            )
            if len(searched_album) == 0:
                continue
            album_id = searched_album[0]["id"]
            album_name = re.sub(r"[^\w_. -]", "_", album["name"])
            for photo in album["photos"]:
                tasks.append(
                    executor.submit(
                        upload_content,
                        url=f"https://mywebcamroom.com/api/front/users/{id}/albums/{album_id}/photos",
                        path=f"{self.script_location}\\photos\\{album_name}\\{photo["id"]}.jpg",
                        type="photo",
                        data=data,
                        cookies_dict=cookies_dict
                    )
                )
        concurrent.futures.wait(tasks)

    def upload_all_videos(
        self, driver, login, id, csrfNotify, csrfTimestamp, csrfToken
    ):
        executor = concurrent.futures.ThreadPoolExecutor()
        tasks = []
        cookies = driver.get_cookies()
        cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
        for video in self.model_profile["videos"]:
            tasks.append(
                    executor.submit(
                        upload_video,
                        video = video,
                        path = self.script_location + f'\\videos\\{video["id"]}.mp4',
                        modelId = id,
                        cookies_dict = cookies_dict,
                        csrfNotify = csrfNotify,
                        csrfTimestamp = csrfTimestamp,
                        csrfToken = csrfToken
                    )
                )
        concurrent.futures.wait(tasks)

    def change_show_activities(
        self, driver: Chrome, id, csrfNotify, csrfTimestamp, csrfToken
    ):
        driver.execute_script(
            'await fetch("https://mywebcamroom.com/api/front/users/'
            + str(id)
            + '",{body:JSON.stringify(arguments[0])'
            + ',method:"POST",mode:"cors",credentials:"include"});',
            dict(
                list(
                    self.model_profile["broadcast_settings"]["show_activities"].items()
                )
                + list(
                    {
                        "csrfNotifyTimestamp": csrfNotify,
                        "csrfTimestamp": csrfTimestamp,
                        "csrfToken": csrfToken,
                    }.items()
                )
            ),
        )

    def change_prices(self, driver: Chrome, id, csrfNotify, csrfTimestamp, csrfToken):
        driver.execute_script(
            'await fetch("https://mywebcamroom.com/api/front/users/'
            + str(id)
            + '",{body:JSON.stringify(arguments[0])'
            + ',method:"POST",mode:"cors",credentials:"include"});',
            dict(
                list(self.model_profile["broadcast_settings"]["pricing"].items())
                + list(
                    {
                        "csrfNotifyTimestamp": csrfNotify,
                        "csrfTimestamp": csrfTimestamp,
                        "csrfToken": csrfToken,
                    }.items()
                )
            ),
        )

    def change_cover_image(self, driver, login, id):
        coverUrl = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/v2/config?uniq=",{mode:"cors",credentials:"include"}).then(n=>n.json()).then(n=>n.data.user.sourcePreviewUrl);'
        )
        driver.get(f"https://mywebcamroom.com/{login}")
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                ("css selector", 'div[data-nav-item="information"]')
            )
        )
        driver.execute_script("arguments[0].click()", element)
        uploadBtn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    "css selector",
                    "button.cover-picture-action-button",
                )
            )
        )
        self.scroll_to_elem(driver, uploadBtn)
        uploadBtn.click()
        sleep(2)
        self.keyboard.type(self.script_location + f"\\profile\\cover_image.jpg")
        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter)
        for i in range(60):
            if coverUrl != driver.execute_script(
                'return await fetch("https://mywebcamroom.com/api/front/v2/config?uniq=",{mode:"cors",credentials:"include"}).then(n=>n.json()).then(n=>n.data.user.sourcePreviewUrl);'
            ):
                break
            else:
                sleep(2)
        else:
            print("Too long wait for message that new video is uploaded")

    def change_record_settings(
        self, driver: Chrome, id, csrfNotify, csrfTimestamp, csrfToken
    ):
        driver.execute_script(
            'await fetch("https://mywebcamroom.com/api/front/users/'
            + str(id)
            + '",{body:JSON.stringify(arguments[0])'
            + ',method:"POST",mode:"cors",credentials:"include"});',
            dict(
                list(self.model_profile["broadcast_settings"]["record"].items())
                + list(
                    {
                        "csrfNotifyTimestamp": csrfNotify,
                        "csrfTimestamp": csrfTimestamp,
                        "csrfToken": csrfToken,
                    }.items()
                )
            ),
        )

    def change_tip_menu(self, driver: Chrome, id, csrfNotify, csrfTimestamp, csrfToken):
        driver.execute_script(
            'await fetch("https://mywebcamroom.com/api/front/models/'
            + str(id)
            + "/tip/menu"
            + '",{body:JSON.stringify(arguments[0])'
            + ',method:"PUT",mode:"cors",credentials:"include"});',
            dict(
                list(self.model_profile["broadcast_settings"]["tip_menu"].items())
                + list(
                    {
                        "csrfNotifyTimestamp": csrfNotify,
                        "csrfTimestamp": csrfTimestamp,
                        "csrfToken": csrfToken,
                    }.items()
                )
            ),
        )

    def change_extensions_settings(
        self, driver: Chrome, id, csrfNotify, csrfTimestamp, csrfToken
    ):
        for extension in self.model_profile["broadcast_settings"]["extensions"]:
            if extension["name"] == "announcement-bot":
                continue
            driver.execute_script(
                'await fetch("https://mywebcamroom.com/api/front/models/'
                + str(id)
                + '/apps/",{headers:{"content-type":"application/json","sec-fetch-dest":"empty","sec-fetch-mode":"cors","sec-fetch-site":"same-origin"},referrerPolicy:"strict-origin-when-cross-origin",body:JSON.stringify(arguments[0]),method:"POST",mode:"cors",credentials:"include"});',
                {
                    "appId": extension["id"],
                    "csrfNotifyTimestamp": csrfNotify,
                    "csrfTimestamp": csrfTimestamp,
                    "csrfToken": csrfToken,
                },
            )
            driver.execute_script(
                'await fetch("https://mywebcamroom.com/api/front/models/'
                + str(id)
                + "/apps/"
                + str(extension["id"])
                + '",{body:JSON.stringify(arguments[0])'
                + ',method:"PUT",mode:"cors",credentials:"include"});',
                {
                    "settings": extension["modelSettings"]["settings"],
                    "isEnabled": extension["modelSettings"]["isEnabled"],
                    "csrfNotifyTimestamp": csrfNotify,
                    "csrfTimestamp": csrfTimestamp,
                    "csrfToken": csrfToken,
                },
            )

    def upload_teaser(self, driver: Chrome, login, id):
        if self.model_profile["broadcast_settings"]["teaser"] == False:
            return
        teaserUrl = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/users/'
            + str(id)
            + '?uniq=",{mode:"cors",credentials:"include"}).then(e=>e.json()).then(e=>e?.teaser?.url);'
        )
        driver.get(f"https://mywebcamroom.com/{login}")
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                ("css selector", 'div[data-nav-item="information"]')
            )
        )
        driver.execute_script("arguments[0].click()", element)
        uploadBtn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    "css selector",
                    "button.teaser-upload-button, div.teaser-uploader-player__actions button.cover-picture-action-button",
                )
            )
        )
        self.scroll_to_elem(driver, uploadBtn)
        uploadBtn.click()
        sleep(2)
        self.keyboard.type(self.script_location + f"\\videos\\teaser.mp4")
        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter)
        for i in range(120):
            if teaserUrl != driver.execute_script(
                'return await fetch("https://mywebcamroom.com/api/front/users/'
                + str(id)
                + '?uniq=",{mode:"cors",credentials:"include"}).then(e=>e.json()).then(e=>e?.teaser?.url);'
            ):
                break
            else:
                sleep(2)
        else:
            print("Too long wait for message that new video is uploaded")

    def start_transfer(self, login, password, login2, password2, config):
        driver = Driver(
            uc=True,
            guest_mode=True,
            headless=False,
            chromium_arg="--lang=en-US",
            undetectable=True,
            disable_csp=True,
            uc_subprocess=True,
        )
        driver.maximize_window()
        output = ""
        self.login_stripchat(driver, login, password)
        modelId = driver.execute_script(
            "return fetch(`${window.location.origin}/api/front/v2/config`).then(res => res.json()).then(e => e.data.user.id)"
        )
        config["my_info"] and self.copy_my_info(driver, modelId)
        config["videos"] and self.download_all_videos(driver, login)
        config["photos"] and self.download_all_photos(driver, login)
        if config["broadcast_settings"]:
            config["broadcast_settings"]["teaser_video"] and self.download_teaser_video(
                driver, modelId
            )
            any(config["broadcast_settings"].values()) and self.copy_broadcast_settings(
                driver, modelId
            )
            config["broadcast_settings"]["extensions"] and self.copy_extensions(
                driver, modelId
            )
        driver.delete_all_cookies()

        """ Done with parsing all data... """
        pprint(self.model_profile)

        self.login_stripchat(driver, login2, password2)
        modelId = driver.execute_script(
            "return await fetch(`${window.location.origin}/api/front/v2/config`).then(res => res.json()).then(e => e.data.user.id)"
        )
        configData = driver.execute_script(
            'return await fetch("https://mywebcamroom.com/api/front/v2/config/data?timezoneOffset=-180&timezone=Europe%2FMoscow&uniq=",{credentials:"include"}).then(e=>e.json()).then(e=>e.data);'
        )
        if config["my_info"]:
            try:
                config["my_info"]["main_bio"] and self.change_my_info(
                    driver,
                    modelId,
                    configData["csrfNotifyTimestamp"],
                    configData["csrfTimestamp"],
                    configData["csrfToken"],
                )
            except Exception as ex:
                output += f"Main bio error\n{str(ex)}\n"
            try:
                config["my_info"]["panels"] and self.add_panels(
                    driver,
                    login2,
                    modelId,
                    configData["csrfNotifyTimestamp"],
                    configData["csrfTimestamp"],
                    configData["csrfToken"],
                )
            except Exception as ex:
                output += f"Panels error\n{str(ex)}\n"
            try:
                config["my_info"]["background"] and self.upload_background(
                    driver, login2, modelId
                )
            except Exception as ex:
                output += f"Background error\n{str(ex)}\n"
        try:
            config["videos"] and self.upload_all_videos(
                driver,
                login2,
                modelId,
                configData["csrfNotifyTimestamp"],
                configData["csrfTimestamp"],
                configData["csrfToken"],
            )
        except Exception as ex:
            output += f"Videos error\n{str(ex)}\n"
        try:
            config["photos"] and self.upload_all_photos(
                driver,
                login2,
                modelId,
                configData["csrfNotifyTimestamp"],
                configData["csrfTimestamp"],
                configData["csrfToken"],
            )
        except Exception as ex:
            output += f"Photos error\n{str(ex)}\n"
        if config["broadcast_settings"]:
            try:
                config["broadcast_settings"][
                    "show_activities"
                ] and self.change_show_activities(
                    driver,
                    modelId,
                    configData["csrfNotifyTimestamp"],
                    configData["csrfTimestamp"],
                    configData["csrfToken"],
                )
            except Exception as ex:
                output += f"Show activities error\n{str(ex)}\n"
            try:
                config["broadcast_settings"]["teaser_video"] and self.upload_teaser(
                    driver, login2, modelId
                )
            except Exception as ex:
                output += f"Teaser video transfer error\n{str(ex)}\n"
            try:
                config["broadcast_settings"]["prices"] and self.change_prices(
                    driver,
                    modelId,
                    configData["csrfNotifyTimestamp"],
                    configData["csrfTimestamp"],
                    configData["csrfToken"],
                )
            except Exception as ex:
                output += f"Prices error\n{str(ex)}\n"
            try:
                config["broadcast_settings"]["cover_image"] and self.change_cover_image(
                    driver, login2, modelId
                )
            except Exception as ex:
                output += f"Cover image error\n{str(ex)}\n"
            try:
                config["broadcast_settings"][
                    "record_show"
                ] and self.change_record_settings(
                    driver,
                    modelId,
                    configData["csrfNotifyTimestamp"],
                    configData["csrfTimestamp"],
                    configData["csrfToken"],
                )
            except Exception as ex:
                output += f"Record show error\n{str(ex)}\n"
            try:
                config["broadcast_settings"]["tip_menu"] and self.change_tip_menu(
                    driver,
                    modelId,
                    configData["csrfNotifyTimestamp"],
                    configData["csrfTimestamp"],
                    configData["csrfToken"],
                )
            except Exception as ex:
                output += f"Tip menu error\n{str(ex)}\n"
            try:
                config["broadcast_settings"][
                    "extensions"
                ] and self.change_extensions_settings(
                    driver,
                    modelId,
                    configData["csrfNotifyTimestamp"],
                    configData["csrfTimestamp"],
                    configData["csrfToken"],
                )
            except Exception as ex:
                output += f"Extensions error\n{str(ex)}\n"
        driver.quit()
        return output
