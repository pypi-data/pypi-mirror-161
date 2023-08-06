from webform.formcontrol import WebElement


class Login:
    def __init__(self, account, password, security_answers: dict):
        self.account = account
        self.password = password
        self.security_answers = security_answers
        self.web_element = WebElement()

    @property
    def actions(self):
        return [self.login, self.securityCheck, self.acknowlege]

    @property
    def login(self):

        url = "https://tfwp-jb.lmia.esdc.gc.ca/employer/"
        next_page_tag1 = "#loginForm\\:j_id_43"

        login_id = "#loginForm\\:j_id_43"
        account_id = "#loginForm\\:input-email"
        password_id = "#loginForm\\:input-password"
        next_page_tag2 = "#continueButton"

        actions = [
            self.web_element.gotoPageElement(url, wait_for=next_page_tag1),
            self.web_element.loginElement(
                account_id, self.account, password_id, self.password
            ),
        ]

        return self.web_element.pageElement(
            login_id, next_page_tag2, actions, label="Login"
        )

    @property
    def securityCheck(self):
        security_label_id = "#securityForm > fieldset > div > p"
        security_answer_id = "#securityForm\\:input-security-answer"
        actions = [
            self.web_element.securityElement(
                security_label_id,
                security_answer_id,
                self.security_answers,
            )
        ]
        continue_button = "#continueButton"
        next_page_tag = "#modal-accept"
        return self.web_element.pageElement(
            continue_button, next_page_tag, actions, label="Security question check"
        )

    @property
    def acknowlege(self):
        accept_button = "#modal-accept"
        next_page_tag = "#wb-auto-6_filter > label > input[type=search]"  # Filter
        return WebElement().pageElement(
            accept_button, next_page_tag, [], label="Acknowlege important message"
        )
