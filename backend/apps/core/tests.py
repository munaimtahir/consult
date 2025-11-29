from django.test import TestCase
from django.urls import reverse

class CoreTests(TestCase):
    def test_admin_site_is_accessible(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)
