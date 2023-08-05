import ckan.model as model
import pytest

from ckanext.check_link.model import Report


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestReport:
    def test_removed_with_resource(self, resource, faker):
        report = Report(url=faker.url(), resource_id=resource["id"], state="unknown")
        model.Session.add(report)
        model.Session.commit()

        assert report.id

        model.Session.delete(model.Resource.get(resource["id"]))
        model.Session.commit()
        assert not model.Session.query(Report).filter_by(id=report.id).one_or_none()
        assert not Report.by_resource_id(resource["id"])

    def test_by_resource_id(self, report_factory, resource):
        with_resource = report_factory(resource_id=resource["id"])
        report_factory(resource_id=None)

        assert Report.by_resource_id(resource["id"]).id == with_resource["id"]
        assert not Report.by_resource_id(None)

    def test_by_url(self, report_factory):
        first = report_factory()
        second = report_factory(resource_id=None)

        assert not Report.by_url(first["url"])
        assert Report.by_url(second["url"]).id == second["id"]
