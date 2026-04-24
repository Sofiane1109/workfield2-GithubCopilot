"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a TestClient instance for testing"""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities"""
        response = client.get("/activities")
        activities = response.json()
        
        # Verify we get a dictionary with activities
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Verify specific activities exist
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_activity_object_structure(self, client):
        """Test that each activity has the required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        # Check any activity object structure
        activity = activities["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_participants_list_format(self, client):
        """Test that participants is a list of strings (emails)"""
        response = client.get("/activities")
        activities = response.json()
        
        # Verify participants is a list
        participants = activities["Programming Class"]["participants"]
        assert isinstance(participants, list)
        
        # Verify participants contain email strings
        assert all(isinstance(email, str) for email in participants)

    def test_activity_fields_are_expected_types(self, client):
        """Test that activity fields have expected data types"""
        response = client.get("/activities")
        activities = response.json()
        
        activity = activities["Chess Club"]
        assert isinstance(activity["description"], str)
        assert isinstance(activity["schedule"], str)
        assert isinstance(activity["max_participants"], int)
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client):
        """Test successful signup adds email to participants"""
        activity_name = "Chess Club"
        email = "test.student@mergington.edu"
        
        # Get initial participant count
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[activity_name]["participants"])
        
        # Perform signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Verify response
        assert response.status_code == 200
        assert "message" in response.json()
        
        # Verify participant was added
        response_after = client.get("/activities")
        new_count = len(response_after.json()[activity_name]["participants"])
        assert new_count == initial_count + 1

    def test_signup_returns_success_message(self, client):
        """Test that successful signup returns appropriate message"""
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]

    def test_signup_activity_not_found(self, client):
        """Test signup returns 404 for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_signup_allows_duplicate_email(self, client):
        """Test that the same email can be added twice (current behavior)"""
        activity_name = "Gym Class"
        email = "duplicate@mergington.edu"
        
        # First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both emails are in participants list (duplicate exists)
        response_get = client.get("/activities")
        participants = response_get.json()[activity_name]["participants"]
        email_count = participants.count(email)
        assert email_count == 2  # Email appears twice

    def test_signup_email_parameter_required(self, client):
        """Test that signup requires email parameter"""
        activity_name = "Chess Club"
        
        # POST without email parameter should fail
        response = client.post(f"/activities/{activity_name}/signup")
        assert response.status_code != 200  # Should fail without email

    def test_signup_with_special_characters_in_activity_name(self, client):
        """Test signup handles activity names with proper URL encoding"""
        activity_name = "Chess Club"
        email = "student@mergington.edu"
        
        # Even though activity name has space, URL encoding should work
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200

    def test_signup_response_status_codes(self, client):
        """Test that signup returns correct status codes"""
        # Test 200 for success
        response_success = client.post(
            "/activities/Chess Club/signup",
            params={"email": "valid@mergington.edu"}
        )
        assert response_success.status_code == 200
        
        # Test 404 for missing activity
        response_not_found = client.post(
            "/activities/Fake Activity/signup",
            params={"email": "valid@mergington.edu"}
        )
        assert response_not_found.status_code == 404
