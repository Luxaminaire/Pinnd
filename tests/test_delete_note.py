"""Four unit tests for database.delete_note()."""


def test_delete_existing_note(test_db, create_note):
    note_id = create_note()

    result = test_db.delete_note(note_id)

    assert result is True
    assert test_db.get_note(note_id) is None


def test_delete_nonexistent_note(test_db, create_note):
    existing_id = create_note('Keep me')

    result = test_db.delete_note(99999)

    assert result is False
    assert test_db.get_note(existing_id) is not None


def test_delete_same_note_twice(test_db, create_note):
    note_id = create_note()

    first_result = test_db.delete_note(note_id)
    second_result = test_db.delete_note(note_id)

    assert first_result is True
    assert second_result is False
    assert test_db.get_note(note_id) is None


def test_delete_only_selected_note(test_db, create_note):
    first_id = create_note('First')
    selected_id = create_note('Delete this')
    third_id = create_note('Third')

    result = test_db.delete_note(selected_id)

    assert result is True
    assert test_db.get_note(selected_id) is None
    assert test_db.get_note(first_id)['title'] == 'First'
    assert test_db.get_note(third_id)['title'] == 'Third'
    assert len(test_db.notes(1)) == 2
