import ckan.plugins.toolkit as tk
import pytest
from ckan.tests.helpers import call_action


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestSave:
    def test_resource_id_must_be_real(self, resource, faker):
        with pytest.raises(tk.ValidationError):
            call_action(
                "check_link_report_save",
                url=faker.url(),
                state="unknown",
                resource_id=faker.uuid4(),
            )

        call_action(
            "check_link_report_save",
            url=faker.url(),
            state="unknown",
            resource_id=resource["id"],
        )

    def test_url_is_mandatory(self, resource, faker):
        with pytest.raises(tk.ValidationError):
            call_action(
                "check_link_report_save", state="unknown", resource_id=resource["id"]
            )

    def test_state_is_mandatory(self, resource, faker):
        with pytest.raises(tk.ValidationError):
            call_action(
                "check_link_report_save", url=faker.url(), resource_id=resource["id"]
            )

    def test_update_existing_by_resource_id(self, resource, report_factory):
        report = report_factory(resource_id=resource["id"], state="unknown")

        updated = call_action(
            "check_link_report_save",
            url=report["url"],
            resource_id=resource["id"],
            state="updated",
        )

        assert updated["id"] == report["id"]
        assert updated["state"] == "updated"

    def test_update_existing_by_url(self, report_factory):
        report = report_factory(resource_id=None, state="unknown")

        updated = call_action(
            "check_link_report_save", url=report["url"], state="updated"
        )

        assert updated["id"] == report["id"]
        assert updated["state"] == "updated"

    def test_update_existing_by_id(self, report_factory, faker):
        report = report_factory(resource_id=None, state="unknown")

        updated = call_action(
            "check_link_report_save", url=faker.url(), state="updated", id=report["id"]
        )

        assert updated["id"] == report["id"]
        assert updated["state"] == "updated"


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestShow:
    def test_shown_by_id(self, report):
        assert (
            call_action("check_link_report_show", id=report["id"])["id"] == report["id"]
        )
        assert (
            call_action("check_link_report_show", id=report["id"])["id"] == report["id"]
        )

    def test_shown_by_resource_id(self, report_factory):
        with_resource = report_factory()
        assert (
            call_action(
                "check_link_report_show", resource_id=with_resource["resource_id"]
            )["id"]
            == with_resource["id"]
        )

    def test_shown_by_url(self, report_factory):
        with_resource = report_factory()
        without_resource = report_factory(resource_id=None)
        assert (
            call_action("check_link_report_show", url=without_resource["url"])["id"]
            == without_resource["id"]
        )

        with pytest.raises(tk.ObjectNotFound):
            assert call_action("check_link_report_show", url=with_resource["url"])


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestDelete:
    def test_delete(self, report):
        call_action("check_link_report_delete", id=report["id"])
        with pytest.raises(tk.ObjectNotFound):
            assert call_action("check_link_report_show", id=report["id"])


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestSearch:
    def test_limit(self, report_factory):
        report_factory.create_batch(10)

        result = call_action("check_link_report_search", limit=5)
        assert result["count"] == 10
        assert len(result["results"]) == 5

        result = call_action("check_link_report_search", limit=5, offset=8)
        assert result["count"] == 10
        assert len(result["results"]) == 2
