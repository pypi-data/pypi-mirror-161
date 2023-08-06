from abc import ABC, abstractmethod
from webform.formcontrol import WebElement


class WebPages(ABC):
    """Base class for a set of pages"""

    def __init__(self, app: object):
        self.app = app
        self.web_element = WebElement()

    @abstractmethod
    def actions(self):
        """page actions"""


class Page(ABC):
    """Base class for a single page"""

    def __init__(self, page_actions, id, next_page_tag, label="Page") -> None:
        self.page_actions = page_actions
        self.id = id
        self.next_page_tag = next_page_tag
        self.label = label

    @property
    def page(self):
        return WebElement().pageElement(
            self.id, self.next_page_tag, self.page_actions, label=self.label
        )
