import time

from . import Assurka


def pytest_addoption(parser):
    assurka = parser.getgroup('assurka')
    assurka.addoption("--assurka-projectId", action="store", default=None, help="assurka studio project id")
    assurka.addoption("--assurka-secret", action="store", default=None, help="assurka studio project secret id")
    assurka.addoption("--assurka-testPlanId", action="store", default=None, help="assurka studio test plan id")
    assurka.addoption("--assurka-host", action="store", default=None, help="assurka studio host url")


class AssurkaPytest:
    a = Assurka()

    def __init__(self, config):
        self.config = config
        self.projectId = None
        self.secret = None
        self.testPlanId = None
        self.testRunId = None
        self.specs = {}
        self.activate = False

    def pytest_sessionstart(self, session):
        # check to make sure we have the relevant options configured
        if hasattr(session.config.option, 'assurka_projectId'):
            self.projectId = session.config.option.assurka_projectId

        if hasattr(session.config.option, 'assurka_secret'):
            self.secret = session.config.option.assurka_secret

        if hasattr(session.config.option, 'assurka_testPlanId'):
            self.testPlanId = session.config.option.assurka_testPlanId

        if hasattr(session.config.option, 'assurka_host'):
            self.a.urlBase = session.config.option.assurka_host

        if self.secret is not None:
            self.activate = True

    def pytest_collection_modifyitems(self, session, config, items):
        if self.activate is True:
            # authenticate to assurka studio
            self.a.assurka_login(self.projectId, self.secret)
            # get the test plan and params
            self.a.assurka_getTestPlan(self.projectId, self.testPlanId)
            self.a.assurka_getTestPlanParams(self.testPlanId)

            for item in items:
                title = item.nodeid
                path = item.location[0]
                if item.obj.__doc__ is not None:
                    description = item.obj.__doc__.strip()
                else:
                    description = ''
                markers = ','.join([m.name for m in item.iter_markers()])
                self.specs.setdefault(path, []).append({
                    'path': path,
                    'title': title,
                    'description': description,
                    'numFailingTests': 0,
                    'numPassingTests': 0
                })

            # create the assurka test rum
            self.a.assurka_createTestRun(self.testPlanId, {
                'name': 'pytest run',
                'platform': 'pytest',
                'numTotalTestSuites': len(self.specs),
                'numTotalTests': len(items),
                'startTime': time.time()
            })
            self.testRunId = self.a.testRun['id']
            for spec in self.specs:
                s = self.specs[spec]
                # create the new test spec
                self.a.assurka_createTestSpec(self.a.testRun['id'], s[0]['path'])

    def pytest_runtest_logreport(self, report):
        if self.activate is True:
            if report.when == 'call':
                testSpec = next((x for x in self.a.testSpecs if x['name'] == report.location[0]), None)
                spec = self.specs[testSpec['name']]
                for item in spec:
                    if report.passed:
                        item['numPassingTests'] = item['numPassingTests'] + 1
                    else:
                        item['numFailingTests'] = item['numFailingTests'] + 1

                payload = {
                    'testRunId': self.testRunId,
                    'title': report.head_line,
                    'description': report.nodeid,
                    'status': report.outcome,
                    'duration': report.duration,
                    'testSpecId': testSpec['id']
                }
                if hasattr(report.longrepr, 'reprcrash'):
                    payload['failureMessages']: [
                        report.longreprtext
                    ]
                    payload['failureDetails'] = [
                        {
                            'lineno': report.longrepr.reprcrash.lineno,
                            'message': report.longrepr.reprcrash.message
                        }
                        ]

                self.a.assurka_createTestCase(testSpec['id'], payload)

    def pytest_sessionfinish(self, session):
        if self.activate is True:
            for testSpec in self.a.testSpecs:
                spec = self.specs[testSpec['name']][0]
                self.a.assurka_updateTestSpec(self.testRunId, testSpec['id'], {
                    'numPassingTests': spec['numPassingTests'],
                    'numFailingTests': spec['numFailingTests']
                })

            payload = {
                'numTotalTests': session.testscollected,
                'numFailedTests': session.testsfailed,
                'numPassedTests': session.testscollected - session.testsfailed
            }
            self.a.assurka_updateTestRun(self.testPlanId, self.testRunId, payload)
