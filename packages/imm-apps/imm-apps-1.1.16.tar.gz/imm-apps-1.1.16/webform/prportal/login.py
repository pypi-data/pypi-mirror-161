from webform.definition import Action
import base64


class Login:
    def __init__(self, rcic_account):
        self.rcic_account = rcic_account

    def encode(self, password):
        password_bytes = password.encode("ascii")
        base64_bytes = base64.b64encode(password_bytes)
        return base64_bytes.decode("ascii")

    def login(self):
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Sign in",
                "actions": [
                    {
                        "action_type": Action.GotoPage.value,
                        "url": "https://prson-srpel.apps.cic.gc.ca/en/rep/login",
                    },
                    {
                        "action_type": Action.Login.value,
                        "label": "Login",
                        "account": self.rcic_account["account"],
                        "password": self.encode(self.rcic_account["password"]),
                        "account_element_id": "#username",
                        "password_element_id": "#password",
                    },
                ],
                "id": "body > pra-root > pra-localized-app > main > div > pra-login-page > pra-login > div > div > form > button",
                "next_page_tag": "body > pra-root > pra-localized-app > main > div > pra-home-page > div > div > div > pra-card:nth-child(1) > div > div > div > a.btn.btn-secondary.card__all-apps-btn",
            },
            {
                "action_type": Action.WebPage.value,
                "page_name": "Select existing application",
                "actions": [],
                "id": "body > pra-root > pra-localized-app > main > div > pra-home-page > div > div > div > pra-card:nth-child(1) > div > div > div > a.btn.btn-secondary.card__all-apps-btn",
                "next_page_tag": "body > pra-root > pra-localized-app > main > div > pra-rep-dashboard > div > div.search-row.ng-star-inserted > div > button",
            },
        ]
