import openscreen

DEBUG = True


class TestProjectCreation:
    def test_create_project(self, openscreen_session: openscreen.Openscreen, account_id):
        failed_due_to_permissions = False
        try:
            project = openscreen_session.account(account_id).projects().create({'name': 'Should Fail'})
        except PermissionError:
            failed_due_to_permissions = True
        except Exception:
            pass
        assert failed_due_to_permissions == True

    def test_get_projects(self, openscreen_session: openscreen.Openscreen, account_id, project_id):
        projects = openscreen_session.account(account_id).projects().get()
        assert projects.numberOfProjects > 0
        assert any(project.projectId == project_id for project in projects.projects)
