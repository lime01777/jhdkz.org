from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from users.models import User
from submissions.models import Submission, Section
from reviews.models import Review, ReviewAssignment


class ReviewModelTests(TestCase):
    """Юнит-тесты моделей Review и ReviewAssignment."""

    def setUp(self):
        section = Section.objects.create(
            title_ru="Клинические исследования",
            slug="clinical",
            is_active=True,
        )
        self.author = User.objects.create_user(
            username="author2",
            password="pass",
            role="author",
            email="author2@example.com",
        )
        self.reviewer = User.objects.create_user(
            username="reviewer2",
            password="pass",
            role="reviewer",
            email="reviewer2@example.com",
        )
        self.editor = User.objects.create_user(
            username="editor2",
            password="pass",
            role="editor",
            email="editor2@example.com",
        )
        self.submission = Submission.objects.create(
            section=section,
            title_ru="Пилотное исследование",
            abstract_ru="Аннотация",
            keywords_ru="ключевые слова",
            language="ru",
            manuscript_file=SimpleUploadedFile(
                "pilot.pdf",
                b"%PDF-1.4 pilot",
                content_type="application/pdf",
            ),
            corresponding_author=self.author,
            status="submitted",
        )

    def test_review_assignment_overdue_and_accept_decline(self):
        assignment = ReviewAssignment.objects.create(
            submission=self.submission,
            reviewer=self.reviewer,
            assigned_by=self.editor,
            status="pending",
            review_due=timezone.now() - timedelta(days=1),
        )
        self.assertTrue(assignment.is_overdue())

        assignment.accept()
        self.assertEqual(assignment.status, "accepted")
        self.assertIsNotNone(assignment.responded_at)

        assignment.decline("Нет времени")
        self.assertEqual(assignment.status, "declined")
        self.assertEqual(assignment.decline_reason, "Нет времени")

    def test_review_complete_updates_status(self):
        assignment = ReviewAssignment.objects.create(
            submission=self.submission,
            reviewer=self.reviewer,
            assigned_by=self.editor,
            status="accepted",
        )
        review = Review.objects.create(
            submission=self.submission,
            reviewer=self.reviewer,
            assignment=assignment,
            recommendation="accept",
            status="in_progress",
        )
        review.complete_review()
        review.refresh_from_db()
        self.assertEqual(review.status, "completed")
        self.assertIsNotNone(review.completed_at)
