import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Initial state of activities for resetting
INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball team for intramural and inter-school games",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Learn tennis skills and participate in friendly matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["rachel@mergington.edu", "james@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop critical thinking and public speaking through competitive debate",
        "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["lucas@mergington.edu"]
    },
    "Science Club": {
        "description": "Explore STEM topics and conduct hands-on science experiments",
        "schedule": "Wednesdays, 3:30 PM - 4:45 PM",
        "max_participants": 22,
        "participants": ["aisha@mergington.edu", "noah@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu"]
    },
    "Music Band": {
        "description": "Join the school band and perform at events throughout the year",
        "schedule": "Fridays, 3:30 PM - 4:45 PM",
        "max_participants": 25,
        "participants": ["marcus@mergington.edu", "grace@mergington.edu"]
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    activities.clear()
    activities.update(INITIAL_ACTIVITIES)

client = TestClient(app)

# Tests for GET /

def test_root_redirect():
    """Test that root serves the static index.html."""
    # Arrange - nothing special
    
    # Act
    response = client.get("/")
    
    # Assert
    assert response.status_code == 200
    assert "Mergington High School" in response.text  # check content

# Tests for GET /activities

def test_get_activities():
    """Test retrieving all activities."""
    # Arrange - initial state
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert len(data) == 9  # all activities
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]

# Tests for POST /activities/{activity_name}/signup

def test_signup_success():
    """Test successful signup for an activity."""
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert email in activities[activity]["participants"]

def test_signup_duplicate():
    """Test signup fails if already signed up."""
    # Arrange
    email = "michael@mergington.edu"  # already in Chess Club
    activity = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]
    # Ensure not added again
    assert activities[activity]["participants"].count(email) == 1

def test_signup_invalid_activity():
    """Test signup fails for non-existent activity."""
    # Arrange
    email = "test@test.com"
    activity = "Nonexistent Activity"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

# Tests for DELETE /activities/{activity_name}/participants

def test_unregister_success():
    """Test successful removal from an activity."""
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    assert email in activities[activity]["participants"]
    
    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Removed" in data["message"]
    assert email not in activities[activity]["participants"]

def test_unregister_not_registered():
    """Test unregister fails if not signed up."""
    # Arrange
    email = "notregistered@test.com"
    activity = "Chess Club"
    
    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "not registered" in data["detail"]

def test_unregister_invalid_activity():
    """Test unregister fails for non-existent activity."""
    # Arrange
    email = "test@test.com"
    activity = "Nonexistent Activity"
    
    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]