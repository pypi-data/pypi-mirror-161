import requests



class Assurka(object):
    def __init__(self):
        self.token = None
        self.testRun = None
        self.testPlan = None
        self.testPlanParams = None
        self.testSpec = None
        self.testSpecs = []
        self.urlBase = 'https://api.assurka.io'

    def assurka_login(self, projectId, secret):
        try:
            response = requests.post(self.urlBase + '/auth/api', json={
                'id': projectId, 'secret': secret
            }, headers={'Content-type': 'application/json', 'Accept': 'application/json'})
            self.token = response.json()['token']
        except requests.exceptions.HTTPError as error:
            print(error)

    def assurka_getTestPlan(self, projectId, testPlanId):
        try:
            print(self.token)
            response = requests.get(self.urlBase + '/test-plan/' + projectId + '/get/' + testPlanId,
                                    headers={'Content-type': 'application/json', 'Accept': 'application/json',
                                             'Authorization': 'Bearer ' + self.token})
            self.testPlan = response.json()
        except requests.exceptions.HTTPError as error:
            print(error)

    def assurka_getTestPlanParams(self, testPlanId):
        try:
            response = requests.get(self.urlBase + '/test-param/' + testPlanId + '/list',
                                    headers={'Content-type': 'application/json', 'Accept': 'application/json',
                                             'Authorization': 'Bearer ' + self.token})
            self.testPlanParams = response.json()
        except requests.exceptions.HTTPError as error:
            print(error)

    def assurka_createTestRun(self, testPlanId, payload):
        try:
            response = requests.post(self.urlBase + '/test-run/' + testPlanId + '/create',
                                     json=payload,
                                     headers={'Content-type': 'application/json', 'Accept': 'application/json',
                                              'Authorization': 'Bearer ' + self.token})
            self.testRun = response.json()
        except requests.exceptions.HTTPError as error:
            print(error)

    def assurka_createTestSpec(self, testRunId, name):
        try:
            response = requests.post(self.urlBase + '/test-spec/' + testRunId + '/create',
                                     json={'name': name,
                                           'testRunId': testRunId},
                                     headers={'Content-type': 'application/json', 'Accept': 'application/json',
                                              'Authorization': 'Bearer ' + self.token})
            self.testSpec = response.json()
            self.testSpecs.append(response.json())
        except requests.exceptions.HTTPError as error:
            print(error)

    def assurka_createTestCase(self, testSpecId, payload):
        try:
            response = requests.post(self.urlBase + '/test-case/' + testSpecId + '/create',
                                     json=payload,
                                     headers={'Content-type': 'application/json', 'Accept': 'application/json',
                                              'Authorization': 'Bearer ' + self.token})
        except requests.exceptions.HTTPError as error:
            print(error)

    def assurka_updateTestRun(self, testPlanId, testRunId, payload):
        try:
            response = requests.patch(self.urlBase + '/test-run/' + testPlanId + '/update/' + testRunId,
                                      json=payload,
                                      headers={'Content-type': 'application/json', 'Accept': 'application/json',
                                               'Authorization': 'Bearer ' + self.token})
            self.testRun = response.json()
        except requests.exceptions.HTTPError as error:
            print(error)

    def assurka_updateTestSpec(self, testRunId, testSpecId, payload):
        try:
            response = requests.patch(self.urlBase + '/test-spec/' + testRunId + '/update/' + testSpecId,
                                      json=payload,
                                      headers={'Content-type': 'application/json', 'Accept': 'application/json',
                                               'Authorization': 'Bearer ' + self.token})
        except requests.exceptions.HTTPError as error:
            print(error)

    def assurka_updateTestPlan(self, projectId, testPlanId, payload):
        try:
            response = requests.patch(self.urlBase + '/test-plan/' + projectId + '/update/' + testPlanId,
                                      json=payload,
                                      headers={'Content-type': 'application/json', 'Accept': 'application/json',
                                               'Authorization': 'Bearer ' + self.token})
            self.testPlan = response.json()
        except requests.exceptions.HTTPError as error:
            print(error)

    def assurka_updateTestRunCoverage(self, testPlanId, testRunId, payload):
        try:
            response = requests.patch(self.urlBase + '/test-run/' + testPlanId + '/update/' + testRunId + '/coverage',
                                      json=payload,
                                      headers={'Content-type': 'application/json', 'Accept': 'application/json',
                                               'Authorization': 'Bearer ' + self.token})

        except requests.exceptions.HTTPError as error:
            print(error)

