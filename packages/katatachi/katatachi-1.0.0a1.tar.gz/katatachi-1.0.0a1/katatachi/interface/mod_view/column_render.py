from abc import ABCMeta
from abc import abstractmethod
from enum import Enum
from typing import Dict, List


class ModViewColumnRender(metaclass=ABCMeta):
    @abstractmethod
    def render_type(self) -> str:
        pass

    @abstractmethod
    def render_data(self) -> Dict:
        pass


class Text(ModViewColumnRender):
    def __init__(self, text: str):
        self.text = text

    def render_type(self) -> str:
        return "text"

    def render_data(self) -> Dict:
        return {"text": self.text}


class Image(ModViewColumnRender):
    def __init__(self, url: str):
        self.url = url

    def render_type(self) -> str:
        return "image"

    def render_data(self) -> Dict:
        return {"url": self.url}


class ImageList(ModViewColumnRender):
    def __init__(self, urls: List[str]):
        self.urls = urls

    def render_type(self) -> str:
        return "image_list"

    def render_data(self) -> Dict:
        return {"urls": self.urls}


class ButtonAfterCallbackBehavior(Enum):
    Reload = "reload"
    RemoveRow = "remove"
    Nothing = "nothing"


class Button(ModViewColumnRender):
    def __init__(self, text: str, after_callback: ButtonAfterCallbackBehavior):
        self.text = text
        self.after_callback = after_callback

    def render_type(self) -> str:
        return "button"

    def render_data(self) -> Dict:
        return {"text": self.text, "after_callback": self.after_callback.value}


class Video(ModViewColumnRender):
    def __init__(self, url: str):
        self.url = url

    def render_type(self) -> str:
        return "video"

    def render_data(self) -> Dict:
        return {"url": self.url}
