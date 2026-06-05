import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@test.com",
        password="testpass123"
    )


@pytest.mark.django_db
def test_product_list_is_public(client):
    response = client.get("/api/products/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_cart_requires_auth(client):
    response = client.get("/api/cart/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_cart_accessible_when_logged_in(client, user):
    client.force_authenticate(user=user)
    response = client.get("/api/cart/")
    assert response.status_code == 200