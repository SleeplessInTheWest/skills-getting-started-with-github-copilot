ACTIVITY = "Chess Club"
NEW_EMAIL = "newstudent@mergington.edu"
EXISTING_EMAIL = "michael@mergington.edu"


def get_participants(client, activity=ACTIVITY):
    return client.get("/activities").json()[activity]["participants"]


def test_root_redirects_to_static_index(client):
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert ACTIVITY in data
    assert len(data) >= 1
    for details in data.values():
        assert expected_fields <= details.keys()


def test_signup_adds_participant(client):
    # Arrange
    assert NEW_EMAIL not in get_participants(client)

    # Act
    response = client.post(f"/activities/{ACTIVITY}/signup", params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {NEW_EMAIL} for {ACTIVITY}"}
    assert NEW_EMAIL in get_participants(client)


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    activity = "Nonexistent Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_returns_400(client):
    # Arrange
    assert EXISTING_EMAIL in get_participants(client)
    count_before = len(get_participants(client))

    # Act
    response = client.post(f"/activities/{ACTIVITY}/signup", params={"email": EXISTING_EMAIL})

    # Assert
    assert response.status_code == 400
    assert len(get_participants(client)) == count_before


def test_unregister_removes_participant(client):
    # Arrange
    assert EXISTING_EMAIL in get_participants(client)

    # Act
    response = client.delete(f"/activities/{ACTIVITY}/signup", params={"email": EXISTING_EMAIL})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {EXISTING_EMAIL} from {ACTIVITY}"}
    assert EXISTING_EMAIL not in get_participants(client)


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    activity = "Nonexistent Club"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": EXISTING_EMAIL})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_student_not_signed_up_returns_404(client):
    # Arrange
    assert NEW_EMAIL not in get_participants(client)

    # Act
    response = client.delete(f"/activities/{ACTIVITY}/signup", params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_state_is_reset_between_tests(client):
    # Arrange: earlier tests removed and added participants for ACTIVITY

    # Act
    participants = get_participants(client)

    # Assert
    assert EXISTING_EMAIL in participants
    assert NEW_EMAIL not in participants
