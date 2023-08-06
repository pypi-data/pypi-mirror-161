from webform.webcommon import WebPages, Page
import glob


class Upload(WebPages):
    directory: str

    def __init__(self, app: object, directory):
        super().__init__(app)
        self.directory = directory

    @property
    def actions(self):
        return [self.page1]

    @property
    def page1(self):
        recruit_id = "#RecruitmentEffort"
        other_id = "#Other"
        file_list = glob.glob(self.directory + "/*")

        actions = []
        file_list.sort()
        for file in file_list:
            if self.app.lmiacase.stream_of_lmia != "LWS" "recruit" in file.lower():
                self.upload(recruit_id, actions, file)
                actions.append(self.click_upload)
            else:
                self.upload(other_id, actions, file)
                actions.append(self.click_upload)

        next_page_tag = None  # "#attestation"
        return Page(actions, "#summary", next_page_tag, label="upload documents").page

    def upload(self, id, actions, file):
        upload = self.web_element.uploadElement(id, file, label=file)
        actions.append((upload))

    @property
    def click_upload(self):
        return self.web_element.buttonElement("#uploadDocument", label="Upload button")
