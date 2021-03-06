from notes import models as notes_models
from notes.adapters.storage import Storage


class DjangoStorage(Storage):
    """Adapter to use Django ORM as a storage backend."""

    def save_board(self, board):
        """Store board entity."""
        django_board = notes_models.Board.objects.from_entity(board)
        django_board.save()
        return django_board.to_entity()

    def save_board_user(self, board_id, user_id, role):
        """Give user access to a board, or change user's role on board."""
        board_user = notes_models.BoardUser.objects.create(
            board_id=board_id, user_id=user_id, role=role
        )
        return board_user.board.to_entity()

    def get_role(self, user_id, board_id):
        """Get user's role on a board. Returns none if user is not on board."""
        try:
            rel = notes_models.BoardUser.objects.get(user_id=user_id, board_id=board_id)
        except notes_models.BoardUser.DoesNotExist:
            return None
        return rel.role

    def save_note(self, note):
        """Store note entity."""
        django_note = notes_models.Note.objects.from_entity(note)
        django_note.save()
        return django_note.to_entity()

    def get_note(self, id):
        """Retrieve note entity by ID."""
        try:
            django_note = notes_models.Note.objects.get(id=id)
        except notes_models.Note.DoesNotExist:
            raise self.DoesNotExist("Note {} was not found.".format(id))

        return django_note.to_entity()

    def delete_note(self, id):
        """Permanently delete note by ID."""
        try:
            django_note = notes_models.Note.objects.get(id=id)
        except notes_models.Note.DoesNotExist:
            raise self.DoesNotExist("Note {} was not found.".format(id))

        return django_note.delete()

    def get_board(self, id):
        """Get board metadata."""
        try:
            django_note = notes_models.Board.objects.get(id=id, status="active")
        except notes_models.Board.DoesNotExist:
            raise self.DoesNotExist("Board {} was not found.".format(id))

        return django_note.to_entity()

    def get_board_notes(self, id):
        """Get notes within a board."""
        django_notes = notes_models.Note.objects.filter(board_id=id).all()
        return [note.to_entity() for note in django_notes]

    def get_board_users(self, id):
        """Get list of users that are joined to a board."""
        django_board_users = notes_models.BoardUser.objects.filter(board_id=id).all()
        return [
            {"board_id": u.board_id, "id": u.user_id, "role": u.role}
            for u in django_board_users
        ]

    def delete_board_user(self, user_id, board_id):
        try:
            django_board_user = notes_models.BoardUser.objects.get(
                user_id=user_id, board_id=board_id
            )
        except notes_models.BoardUser.DoesNotExist:
            raise self.DoesNotExist(
                "User {} is not joined to board {}".format(user_id, board_id)
            )

        django_board_user.delete()
        return django_board_user.asdict()

    def delete_board(self, id):
        try:
            django_board = notes_models.Board.objects.get(id=id)
        except notes_models.Board.DoesNotExist:
            raise self.DoesNotExist("Board {} does not exist.".format(id))

        django_board.status = "deleted"
        django_board.save()

        return django_board.to_entity()
