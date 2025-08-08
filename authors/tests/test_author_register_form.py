from unittest import TestCase
from django.test import TestCase as DjangoTesteCase
from authors.forms import RegisterForm
from django.contrib.auth.models import User
from parameterized import parameterized
from django.urls import reverse


class AuthorRegisterFormUnitTest(TestCase):
    @parameterized.expand([
        ('first_name', 'Ex.: John'),
        ('last_name', 'Ex.: Doe'),
        ('username', 'Type your username here'),
        ('email', 'Type your e-mail here'),
        ('password', 'Type your password here'),
        ('password2', 'Repeat your password'),
    ])
    def test_fields_placeholder(self, field, current_placeholder):
        form = RegisterForm()
        placeholder = form[field].field.widget.attrs['placeholder']
        self.assertEqual(current_placeholder, placeholder)

    @parameterized.expand([
        ('first_name', 'First Name'),
        ('last_name', 'Last Name'),
        ('username', 'Username*'),
        ('email', 'E-mail*'),
        ('password', 'Password*'),
        ('password2', 'Confirm Password*'),
    ])
    def test_fields_labels(self, field, needed):
        form = RegisterForm()
        current = form[field].field.label
        self.assertEqual(needed, current)


class AuthorRegisterFormIntegrationTest(DjangoTesteCase):
    def setUp(self, *args, **kwargs):
        self.form_data = {
            'username': 'user',
            'first_name': 'first',
            'last_name': 'last',
            'email': 'email@anyemail.com',
            'password': 'Str0ngP@ssword1',
            'password2': 'Str0ngP@ssword1',
        }
        return super().setUp(*args, **kwargs)
    
    @parameterized.expand([
        ('username', 'This field must not be empty.'),
        ('email', 'This field must not be empty.'),
        ('password', 'Password must not be empty.'),
        ('password2', 'Password must not be empty.'),
    ])
    def test_fields_cannot_be_empty(self, field, msg):
        self.form_data[field] = ''
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)
        self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get(field))

    def test_username_field_min_length_should_be_4(self):
        self.form_data['username'] = 'A' * 3
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'The username must have a minimum of 4 characters.'
        self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get('username'))

    def test_username_field_max_length_should_be_150(self):
        self.form_data['username'] = 'A' * 151
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'The username must have a maximum of 150 characters.'
        self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get('username'))

    def test_password_field_have_lower_upper_case_letters_and_number(self):
        self.form_data['password'] = 'abc123'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = (
            'Password must have at least one uppercase letter, '
            'one lowercase letter and one number. '
            'The length should be at least 8 characters.'
        )
        self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get('password'))

    def test_password_accepts_strong_format(self):
        self.form_data['password'] = 'Abcd1234'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = (
            'Password must have at least one uppercase letter, '
            'one lowercase letter and one number. '
            'The length should be at least 8 characters.'
        )
        self.assertNotIn(msg, response.content.decode('utf-8'))
        self.assertNotIn(msg, response.context['form'].errors.get('password', []))

    def test_password_and_password_confirmation_are_not_equal(self):
        self.form_data['password'] = 'Abcd1234'
        self.form_data['password2'] = 'Abcd12345'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'The passwords do not match'

        self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get('password2'))

    def test_password_and_password_confirmation_are_equal(self):
        self.form_data['password'] = 'Abcd1234'
        self.form_data['password2'] = 'Abcd1234'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'The passwords do not match'

        self.assertNotIn(msg, response.content.decode('utf-8'))
        self.assertNotIn(msg, response.context['form'].errors.get('password2', []))


    def test_email_is_not_exist(self):
        # Simulation of an email already existing in the database
        User.objects.create_user(
            username='test_email',
            email='test@test.com',
            password='Test1234',
        )
        self.form_data['email'] = 'test@test.com'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'Email already registered'

        self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get('email'))

    def test_send_get_request_to_registration_create_view_returns_404(self):
        url = reverse('authors:register_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_author_created_can_login(self):
        url = reverse('authors:register_create')
        self.form_data.update({
            'username': 'testuser',
            'password': 'Abcd1234',
            'password2': 'Abcd1234',
        })
        self.client.post(url, data=self.form_data, follow=True)
        is_authenticated = self.client.login(
            username='testuser',
            password='Abcd1234'
        )
        self.assertTrue(is_authenticated)