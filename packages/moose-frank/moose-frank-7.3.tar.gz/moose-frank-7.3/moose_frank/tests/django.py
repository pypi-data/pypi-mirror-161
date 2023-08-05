from unittest.case import SkipTest

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ObjectDoesNotExist
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.models.fields import AutoField
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import Promise


def get_local_time_with_delta(delta):
    return timezone.localtime(timezone.now() + delta).time().replace(microsecond=0)


class _AssertNumQueriesEqualOrLessThanContext(CaptureQueriesContext):
    def __init__(self, num, connection):
        self.num = num
        super().__init__(connection)

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)
        if exc_type is not None:
            return

        executed = len(self)
        assert (
            executed <= self.num
        ), "{} queries executed, expected <= {}. Queries were: {}".format(
            executed,
            self.num,
            "\n".join(query["sql"] for query in self.captured_queries),
        )


def assert_num_queries_equal_or_less(num: int):
    conn = connections[DEFAULT_DB_ALIAS]
    return _AssertNumQueriesEqualOrLessThanContext(num, conn)


class URLTestCaseMixin:
    url = None

    def get_url_formatting_kwargs(self):
        return {}

    def get_url(self, **kwargs):
        if not self.url:
            return None

        url_kwargs = self.get_url_formatting_kwargs() or {}
        url_kwargs.update(**kwargs)

        if url_kwargs:
            return self.url.format(**url_kwargs)
        return self.url


class LoginRequiredTestCaseMixin:
    extra_user_fields = {}
    expected_status_code = 200

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = cls.get_login_user()

    @classmethod
    def get_login_user(cls):
        return get_user_model().objects.create_user(
            email="user@mediamoose.nl",
            password="test",
            first_name="Normal",
            last_name="User",
            **cls.extra_user_fields,
        )

    def setUp(self):
        super().setUp()
        assert self.client.login(username="user@mediamoose.nl", password="test")

    def test_login_required(self):
        url = self.get_url()

        resp = self.client.get(url)
        assert resp.status_code == self.expected_status_code

        self.client.logout()

        resp = self.client.get(url)
        assert resp.status_code == 302

        resp = self.client.get(url, follow=True)
        assert resp.status_code == 200
        assert resp.wsgi_request.GET.get("next") == url


class SuperuserRequiredTestCaseMixin(LoginRequiredTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        get_user_model().objects.create_superuser(
            email="superuser@mediamoose.nl",
            password="test",
            first_name="Super",
            last_name="User",
        )

    def setUp(self):
        super().setUp()
        assert self.client.login(username="superuser@mediamoose.nl", password="test")

    def test_superuser_required(self):
        url = self.get_url()

        self.client.login(username="user@mediamoose.nl", password="test")

        resp = self.client.get(url)
        assert resp.status_code == 403


class TemplateViewTestCaseMixin:
    url = None
    url_name = None
    not_allowed_methods = ("post", "put", "patch", "delete")
    x_frame = "DENY"

    def get_url(self):
        return self.url

    def test_url_name(self):
        if not self.url_name:
            raise SkipTest("No `url_name` of view given.")

        if type(self.url_name) == tuple:
            url_name = self.url_name[0]
            url_kwargs = self.url_name[1]
        else:
            url_name = self.url_name
            url_kwargs = None

        assert reverse(url_name, kwargs=url_kwargs) == self.get_url()

    def test_template_view(self):
        url = self.get_url()
        resp = self.client.get(url)

        assert resp.status_code == 200
        assert resp["Content-Type"] == "text/html; charset=utf-8"
        assert resp["X-Frame-Options"] == self.x_frame
        assert resp.content

        self.validate_response(resp)

    def validate_response(self, resp):
        pass

    def test_template_view_redirect(self):
        if not self.get_url()[-1:] == "/":
            return

        url = self.get_url().rstrip("/")
        if not url:
            return

        resp = self.client.get(url)
        assert resp.status_code == 301

        resp = self.client.get(url, follow=True)
        assert resp.status_code == 200

    def test_template_view_not_allowed(self):
        if not self.not_allowed_methods:
            raise SkipTest("All HTTP methods are allowed.")

        url = self.get_url()

        for method in self.not_allowed_methods:
            client_function = getattr(self.client, method)
            resp = client_function(url)
            assert resp.status_code == 405, f"Method '{method}' should not be allowed."


class DetailViewTestCaseMixin(URLTestCaseMixin):
    test_get_absolute_url = False
    test_get_update_url = False
    sitemap_url = None
    not_allowed_methods = ("post", "put", "patch", "delete")
    x_frame = "DENY"
    content_type = "text/html; charset=utf-8"

    def get_item(self):
        raise NotImplementedError

    def setUp(self):
        super().setUp()
        self.item = self.get_item()

        url = self.get_url()
        if not url:
            self.fail("URL is not defined in {}.".format(self.__class__.__name__))

    def get_url_formatting_kwargs(self):
        kwargs = super().get_url_formatting_kwargs()
        kwargs["item"] = self.item
        return kwargs

    def test_object_url(self):
        if not self.test_get_absolute_url:
            raise SkipTest("Object URL not tested.")

        assert hasattr(self.item, "get_absolute_url")

        url = self.item.get_absolute_url()

        assert isinstance(url, str)
        assert url == self.get_url()
        assert url.startswith("/")

    def test_update_url(self):
        if not self.test_get_update_url:
            raise SkipTest("Object update URL not tested.")

        assert hasattr(self.item, "get_update_url")

        url = self.item.get_update_url()

        assert isinstance(url, str)
        assert url == self.get_url()
        assert url.startswith("/")

    def validate_detail_response(self, resp):
        assert resp.context["object"] == self.item

    def test_detail_view(self):
        url = self.get_url()
        resp = self.client.get(url)

        assert resp.status_code == 200
        assert resp["Content-Type"] == self.content_type, (
            f"Content-Type ('{resp['Content-Type']}') should be "
            f"'{self.content_type}'"
        )
        assert resp["X-Frame-Options"] == self.x_frame

        if resp.context is not None:
            assert "object" in resp.context

        self.validate_detail_response(resp)

    def test_detail_view_redirect(self):
        url = self.get_url()
        assert url.endswith("/")

        url = url.rstrip("/")

        resp = self.client.get(url)
        assert resp.status_code == 301

        resp = self.client.get(url, follow=True)
        assert resp.status_code == 200

    def test_detail_view_not_allowed(self):
        url = self.get_url()

        for method in self.not_allowed_methods:
            client_function = getattr(self.client, method)
            resp = client_function(url)
            assert resp.status_code == 405

    def test_in_sitemap(self):
        if not self.sitemap_url:
            raise SkipTest("Inclusion in sitemap not tested.")

        resp = self.client.get(self.sitemap_url)
        assert resp.status_code == 200

        self.assertContains(resp, self.get_url())


class ListViewTestCaseMixin(URLTestCaseMixin):
    test_get_absolute_url = False
    test_get_update_url = False
    not_allowed_methods = ("post", "put", "patch", "delete")
    test_pagination = True
    test_paginate_by = True
    test_object_list = True
    x_frame = "DENY"

    @classmethod
    def get_items(cls):
        raise NotImplementedError

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.items = cls.get_items()

    def test_list_view(self):
        url = self.get_url()
        resp = self.client.get(url)

        if not hasattr(self, "items"):
            self.fail(
                "`{}` has no items, because `setUpTestData` was "
                "not called. Hint: use `TestCase` instead of "
                "`SimpleTestCase`.".format(self.__class__.__name__)
            )

        assert resp.status_code == 200
        assert resp["Content-Type"] == "text/html; charset=utf-8"
        assert resp["X-Frame-Options"] == self.x_frame

        if self.test_object_list:
            assert "object_list" in resp.context
        assert "is_paginated" in resp.context

        if self.test_pagination:
            assert "paginator" in resp.context
        elif self.test_object_list:
            assert all(item in resp.context["object_list"] for item in self.items)

        if self.test_object_list:
            object_set = set(resp.context["object_list"])
            if len(object_set) != len(resp.context["object_list"]):
                self.fail("List view has duplicate objects.")

        if resp.context["view"].paginate_by:
            assert isinstance(
                resp.context["view"].page_kwarg, Promise
            ), "Page kwarg of '{}' is not translated.".format(resp.context["view"])

        self.validate_response(resp)

    def validate_response(self, resp):
        pass

    def test_pages(self):
        if not self.test_pagination:
            raise SkipTest("Pagination not tested.")

        paginate_by = None
        if self.test_paginate_by:
            session = self.client.session
            session["paginate_by"] = paginate_by = 1
            session.save()

        url = self.get_url()
        resp = self.client.get(url)
        page_kwargs = resp.context["view"].page_kwarg
        paginate_by = paginate_by or resp.context["view"].paginate_by
        paginator = resp.context["paginator"]
        page_range = list(paginator.page_range)

        seen = set()
        for index, page_nr in enumerate(page_range, start=1):
            url = self.get_url()
            resp = self.client.get(url, {page_kwargs: page_nr})
            assert resp.status_code == 200
            assert resp["Content-Type"] == "text/html; charset=utf-8"
            assert resp["X-Frame-Options"] == self.x_frame

            assert "page_obj" in resp.context
            assert resp.context["page_obj"].number == index

            page_objects = resp.context["object_list"]

            orphans = resp.context["view"].paginate_orphans
            if orphans:
                if page_nr == page_range[-1]:
                    assert 1 <= len(page_objects) <= paginate_by + orphans, (
                        f"Last page `{page_nr}` should have between "
                        f"[1 .. {paginate_by + orphans}] objects, but it "
                        f"has {len(page_objects)} objects."
                    )
                else:
                    assert len(page_objects) == paginate_by
            else:
                assert len(page_objects) == paginate_by, (
                    f"Page `{page_nr}` should contain {paginate_by} "
                    f"objects, but it has {len(page_objects)} objects."
                )

            page_objects_set = set(page_objects)
            if len(page_objects_set) != len(page_objects):
                self.fail("Page '{}' has duplicate objects.".format(page_nr))

            assert all(page_object in self.items for page_object in page_objects_set), (
                "Page '{}' contains unexpected objects.\n "
                "{!r} \n not in \n {!r}".format(page_nr, page_objects_set, self.items)
            )

            if page_objects_set.intersection(seen):
                self.fail(
                    "Page '{}' contains objects already seen on a"
                    "prior page.".format(page_nr)
                )
            seen.update(page_objects)

        assert len(seen) == len(self.items)

    def test_paginate_by_session(self):
        if not self.test_pagination or not self.test_paginate_by:
            raise SkipTest("Pagination not tested.")

        session = self.client.session
        session["paginate_by"] = 1
        session.save()

        url = self.get_url()
        resp = self.client.get(url)
        paginator = resp.context["paginator"]

        assert 1 <= paginator.num_pages <= len(self.items)

    def test_paginate_by_get_param(self):
        if not self.test_pagination or not self.test_paginate_by:
            raise SkipTest("Pagination not tested.")

        url = self.get_url()
        resp = self.client.get(url, {"aantal": 1})
        session = self.client.session

        assert resp.status_code == 200
        assert "paginate_by" in session
        assert int(session["paginate_by"]) == 1

    def test_invalid_paginate_by_in_session(self):
        if not self.test_pagination or not self.test_paginate_by:
            raise SkipTest("Pagination not tested.")

        session = self.client.session
        session["paginate_by"] = "test"
        session.save()

        url = self.get_url()
        resp = self.client.get(url)
        session = self.client.session

        assert resp.status_code == 200
        assert resp.context["page_obj"].number == 1
        assert session["paginate_by"] != "test"

    def test_invalid_paginate_by_get_param(self):
        if not self.test_pagination or not self.test_paginate_by:
            raise SkipTest("Pagination not tested.")

        url = self.get_url()
        resp = self.client.get(url, {"aantal": "lorem"})
        session = self.client.session

        assert resp.status_code == 200
        assert resp.context["page_obj"].number == 1
        assert session["paginate_by"] != "lorem"

    def test_list_view_redirect(self):
        url = self.get_url().rstrip("/")

        resp = self.client.get(url)
        assert resp.status_code == 301

        resp = self.client.get(url, follow=True)
        assert resp.status_code == 200

    def test_list_view_not_allowed(self):
        url = self.get_url()
        for method in self.not_allowed_methods:
            client_function = getattr(self.client, method)
            resp = client_function(url)
            assert resp.status_code == 405

    def test_object_urls(self):
        if not self.test_get_absolute_url:
            raise SkipTest("Absolute url not tested.")

        assert all(hasattr(item, "get_absolute_url") for item in self.items)
        assert all(bool(item.get_absolute_url()) for item in self.items)

        url = self.get_url()
        resp = self.client.get(url)
        for item in resp.context["object_list"]:
            item_url = item.get_absolute_url()
            self.assertContains(resp, item_url)

    def test_update_urls(self):
        if not self.test_get_update_url:
            raise SkipTest("Update url not tested.")

        assert all(hasattr(item, "get_update_url") for item in self.items)
        assert all(bool(item.get_update_url()) for item in self.items)

        url = self.get_url()
        resp = self.client.get(url, {"aantal": len(self.items)})
        for item in self.items:
            item_url = item.get_update_url()
            self.assertContains(resp, item_url)


class ModelTestCaseMixin:
    test_get_absolute_url = False
    test_get_update_url = False
    test_slug_url = False
    skip_verbose_promise_fields = ()

    def get_item(self):
        raise NotImplementedError

    def setUp(self):
        super().setUp()
        item = self.get_item()
        self.item = item.__class__.objects.get(pk=item.pk)

    def test_unicode(self):
        try:
            str(self.item)
        except Exception:
            self.fail()

    def test_translations(self):
        assert isinstance(
            self.item._meta.verbose_name, Promise
        ), "Verbose name not translated."
        assert isinstance(
            self.item._meta.verbose_name_plural, Promise
        ), "Verbose name plural not translated."

        for field in self.item._meta.get_fields():
            if isinstance(field, (AutoField, GenericForeignKey)) or (
                hasattr(field, "name")
                and field.name in self.skip_verbose_promise_fields
            ):
                continue
            try:
                field = field.field
            except AttributeError:
                pass
            if field.auto_created:
                continue
            assert isinstance(
                field.verbose_name, Promise
            ), "Field '{}' has no translated verbose name".format(field.name)

    def test_slug(self):
        if hasattr(self.item, "slug"):
            assert isinstance(self.item.slug, str)

            if hasattr(self.item, "create_slug"):
                self.item.slug = None
                self.item.create_slug()
                assert isinstance(self.item.slug, str)

            if hasattr(self.item, "get_absolute_url") and self.test_slug_url:
                assert self.item.slug in self.item.get_absolute_url()

    def test_absolute_url(self):
        if not self.test_get_absolute_url:
            raise SkipTest("`get_absolute_url` not tested")
        assert hasattr(self.item, "get_absolute_url")
        assert isinstance(self.item.get_absolute_url(), str)

    def test_update_url(self):
        if not self.test_get_update_url:
            raise SkipTest("`get_update_url` not tested")
        assert hasattr(self.item, "get_update_url")
        assert isinstance(self.item.get_update_url(), str)


class CreateViewTestCaseMixin(URLTestCaseMixin):
    redirect_url = save_and_back_url = None
    not_allowed_methods = ("patch", "delete")
    test_success_message = test_invalid_message = True

    def get_redirect_url(self):
        if not self.redirect_url:
            return None
        return self.redirect_url.format(**self.get_url_formatting_kwargs())

    def get_save_and_back_url(self):
        if not self.save_and_back_url:
            return None
        return self.save_and_back_url.format(**self.get_url_formatting_kwargs())

    def get_form_data(self):
        return None

    def check_created_object(self):
        pass

    def test_create_view(self):
        url = self.get_url()

        resp = self.client.get(url)

        assert resp.status_code == 200
        assert "form" in resp.context

    def test_create_object(self):
        post_data = self.get_form_data()
        if post_data is None:
            return

        url = self.get_url()

        if self.get_redirect_url():
            resp = self.client.post(url, post_data, follow=True)
            self.assertRedirects(resp, self.get_redirect_url())
        else:
            resp = self.client.post(url, post_data, follow=True)
            assert resp.status_code == 200

        if self.test_success_message:
            assert "messages" in resp.context
            assert len(resp.context["messages"]) == 1
            assert any(
                message.level_tag == "success" for message in resp.context["messages"]
            )

        self.check_created_object()

    def get_form_invalid_data(self):
        return None

    def test_invalid_submit(self):
        post_data = self.get_form_invalid_data()
        if post_data is None:
            return

        url = self.get_url()
        resp = self.client.post(url, post_data)

        assert resp.status_code == 200
        assert "form" in resp.context
        assert not resp.context["form"].is_valid()

        if self.test_invalid_message:
            assert "messages" in resp.context
            assert len(resp.context["messages"]) == 1
            assert any(
                message.level_tag == "error" for message in resp.context["messages"]
            )

    def test_create_view_redirect(self):
        url = self.get_url().rstrip("/")

        resp = self.client.get(url)
        assert resp.status_code == 301

        resp = self.client.get(url, follow=True)
        assert resp.status_code == 200

    def test_create_view_not_allowed(self):
        url = self.get_url()

        for method in self.not_allowed_methods:
            client_function = getattr(self.client, method)
            resp = client_function(url)
            assert resp.status_code == 405

    def test_save_and_back(self):
        if not self.save_and_back_url:
            return
        post_data = self.get_form_data()
        post_data.update({"save_and_back": True})

        url = self.get_url()
        resp = self.client.post(url, post_data)

        save_and_back_url = self.get_save_and_back_url()
        assert resp.status_code == 302
        assert resp.url == save_and_back_url


class UpdateViewTestCaseMixin(DetailViewTestCaseMixin):
    not_allowed_methods = ("patch", "delete")
    redirect_url = save_and_back_url = None
    test_success_message = test_invalid_message = True

    def get_redirect_url(self):
        if not self.redirect_url:
            return None
        return self.redirect_url.format(**self.get_url_formatting_kwargs())

    def get_save_and_back_url(self):
        if not self.save_and_back_url:
            return None
        return self.save_and_back_url.format(**self.get_url_formatting_kwargs())

    def test_update_view(self):
        url = self.get_url()
        resp = self.client.get(url)

        assert resp.status_code == 200
        assert "form" in resp.context

    def get_form_data(self):
        return None

    def check_updated_object(self):
        pass

    def test_update_object(self):
        post_data = self.get_form_data()
        if post_data is None:
            return

        url = self.get_url()
        resp = self.client.post(url, post_data, follow=True)
        self.assertRedirects(resp, self.get_redirect_url() or url)

        if self.test_success_message:
            assert "messages" in resp.context
            assert len(resp.context["messages"]) == 1
            assert any(
                message.level_tag == "success" for message in resp.context["messages"]
            )

        self.check_updated_object()

    def get_form_invalid_data(self):
        return None

    def test_invalid_submit(self):
        post_data = self.get_form_invalid_data()
        if post_data is None:
            return

        url = self.get_url()
        resp = self.client.post(url, post_data)

        assert resp.status_code == 200
        assert "form" in resp.context
        assert not resp.context[
            "form"
        ].is_valid(), "Form {!r} should be invalid.".format(resp.context["form"])

        if self.test_invalid_message:
            assert "messages" in resp.context
            assert len(resp.context["messages"]) == 1
            assert any(
                message.level_tag == "error" for message in resp.context["messages"]
            )

    def test_save_and_back(self):
        if not self.save_and_back_url:
            return
        post_data = self.get_form_data()
        post_data.update({"save_and_back": True})

        url = self.get_url()
        resp = self.client.post(url, post_data)

        save_and_back_url = self.get_save_and_back_url()
        assert resp.status_code == 302
        assert resp.url == save_and_back_url


class DeleteViewTestCaseMixin(DetailViewTestCaseMixin):
    not_allowed_methods = ("patch",)
    redirect_url = None
    test_success_message = True

    def get_redirect_url(self):
        if not self.redirect_url:
            return None
        return self.redirect_url.format(**self.get_url_formatting_kwargs())

    def test_delete_view(self):
        url = self.get_url()
        resp = self.client.get(url)

        assert resp.status_code == 200
        assert "can_delete" in resp.context

    def check_deleted_object(self):
        pk = self.item.pk
        assert not self.item.__class__.objects.filter(
            pk=pk
        ).exists(), "Object `{!r}` was not deleted.".format(self.item)

        with self.assertRaises(ObjectDoesNotExist):
            self.item.refresh_from_db()

    def test_delete_object(self):
        url = self.get_url()
        resp = self.client.delete(url, {}, follow=True)
        self.assertRedirects(resp, self.get_redirect_url())

        if self.test_success_message:
            assert "messages" in resp.context
            assert len(resp.context["messages"]) == 1
            assert any(
                message.level_tag == "success" for message in resp.context["messages"]
            )

        self.check_deleted_object()

    def test_post_fallback(self):
        url = self.get_url()
        resp = self.client.post(url, {}, follow=True)
        self.assertRedirects(resp, self.get_redirect_url())

        self.check_deleted_object()


class SitemapTestCaseMixin:
    @classmethod
    def get_items(cls):
        raise NotImplementedError

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.items = cls.get_items()

    def get_url(self):
        return self.url

    def test_sitemap(self):
        resp = self.client.get(self.get_url())

        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/xml"
        self.assertContains(resp, "<loc>", len(self.items))
