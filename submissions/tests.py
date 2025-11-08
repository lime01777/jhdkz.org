from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from users.models import User
from submissions.models import Submission, Section, SubmissionAuthor
from reviews.models import ReviewAssignment
from articles.models import Article
from issues.models import Issue
from submissions.forms import SubmissionAuthorForm


class SubmissionWorkflowTests(TestCase):
    """Интеграционные тесты OJS-подобного workflow подачи и рецензирования."""

    def setUp(self):
        self.section = Section.objects.create(
            title_ru="Исследования",
            slug="research",
            description="Основной раздел",
            is_active=True,
        )
        self.issue = Issue.objects.create(
            year=2025,
            number=1,
            title_ru="Тестовый выпуск",
            status='published',
        )

        self.author = User.objects.create_user(
            username="author",
            password="pass",
            role="author",
            email="author@example.com",
            full_name="Автор А.А.",
        )
        self.coauthor = User.objects.create_user(
            username="coauthor",
            password="pass",
            role="author",
            email="coauthor@example.com",
            full_name="Соавтор С.С.",
        )
        self.editor = User.objects.create_user(
            username="editor",
            password="pass",
            role="editor",
            email="editor@example.com",
            full_name="Редактор Р.Р.",
        )
        self.reviewer = User.objects.create_user(
            username="reviewer",
            password="pass",
            role="reviewer",
            email="reviewer@example.com",
            full_name="Рецензент Р.Р.",
        )

    def _create_manuscript(self):
        return SimpleUploadedFile(
            "manuscript.pdf",
            b"%PDF-1.4 test manuscript content",
            content_type="application/pdf",
        )

    def test_full_submission_review_workflow(self):
        """Автор → отправка; редактор → назначение рецензента; рецензент → рецензия; редактор → решение."""
        self.client.force_login(self.author)

        # Шаг 1: создание подачи
        response = self.client.post(
            reverse("submissions:create"),
            data={
                "section": self.section.pk,
                "title_ru": "Исследование здоровья",
                "title_kk": "",
                "title_en": "Health Research",
                "abstract_ru": "Краткая аннотация.",
                "abstract_kk": "",
                "abstract_en": "",
                "keywords_ru": "здоровье, образование",
                "keywords_kk": "",
                "keywords_en": "",
                "language": "ru",
                "manuscript_file": self._create_manuscript(),
            },
        )
        self.assertEqual(response.status_code, 302)

        submission = Submission.objects.get(corresponding_author=self.author)
        self.assertEqual(submission.status, "draft")

        # Шаг 3: управление авторами (создаёт запись для корреспондирующего автора)
        step3_url = reverse("submissions:step3", kwargs={"pk": submission.pk})
        response = self.client.get(step3_url)
        self.assertEqual(response.status_code, 200)

        submission.refresh_from_db()
        self.assertTrue(submission.submission_authors.filter(author=self.author).exists())

        # Добавляем соавтора
        response = self.client.post(
            step3_url,
            data={
                "author": self.coauthor.pk,
                "author_order": 2,
                "is_principal": "on",
                "affiliation": "Медицинский университет",
                "orcid": "",
                "email": "coauthor@example.com",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            submission.submission_authors.filter(author=self.coauthor).exists()
        )

        # Шаг 5: отправка статьи
        step5_url = reverse("submissions:step5", kwargs={"pk": submission.pk})
        response = self.client.post(step5_url, data={"submit": "submit"})
        self.assertEqual(response.status_code, 302)

        submission.refresh_from_db()
        self.assertEqual(submission.status, "submitted")
        self.assertIsNotNone(submission.submitted_at)
        self.assertEqual(submission.submission_authors.count(), 2)

        # Редактор назначает рецензента
        submission.assigned_editor = self.editor
        submission.save(update_fields=["assigned_editor"])

        self.client.force_login(self.editor)
        assign_url = reverse(
            "reviews:assign_reviewer", kwargs={"submission_pk": submission.pk}
        )
        response = self.client.post(
            assign_url,
            data={
                "reviewer": self.reviewer.pk,
                "review_due": (timezone.now() + timedelta(days=7)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
                "invitation_message": "Просьба выполнить рецензию.",
            },
        )
        self.assertEqual(response.status_code, 302)

        assignment = ReviewAssignment.objects.get(
            submission=submission, reviewer=self.reviewer
        )
        submission.refresh_from_db()
        self.assertEqual(submission.status, "reviewer_assigned")
        self.assertEqual(assignment.status, "pending")

        # Рецензент принимает приглашение
        self.client.force_login(self.reviewer)
        detail_url = reverse(
            "reviews:review_assignment_detail", kwargs={"pk": assignment.pk}
        )
        response = self.client.post(detail_url, data={"accept": "1"})
        self.assertEqual(response.status_code, 302)

        assignment.refresh_from_db()
        self.assertEqual(assignment.status, "accepted")
        self.assertIsNotNone(assignment.review)

        review = assignment.review
        submission.refresh_from_db()
        self.assertEqual(submission.status, "reviewer_assigned")

        # Рецензент заполняет рецензию
        review_url = reverse("reviews:do_review", kwargs={"pk": review.pk})
        response = self.client.post(
            review_url,
            data={
                "originality": 4,
                "scientific_value": 5,
                "methodology": 4,
                "presentation": 4,
                "language_quality": 5,
                "relevance": 5,
                "comments_for_author": "Отличная работа.",
                "comments_for_editor": "Рекомендую принять.",
                "general_comments": "",
                "strengths": "",
                "weaknesses": "",
                "suggestions": "",
                "recommendation": "accept",
                "time_spent": 120,
            },
        )
        self.assertEqual(response.status_code, 302)

        review.refresh_from_db()
        submission.refresh_from_db()
        self.assertEqual(review.status, "completed")
        self.assertEqual(submission.status, "review_completed")

        # Редактор принимает решение
        self.client.force_login(self.editor)
        decision_url = reverse(
            "reviews:make_decision", kwargs={"submission_pk": submission.pk}
        )
        response = self.client.post(
            decision_url,
            data={
                "decision": "accept",
                "comments": "",
                "comments_for_author": "Поздравляем с публикацией!",
                "internal_notes": "",
                "reviews": [str(review.pk)],
            },
        )
        self.assertEqual(response.status_code, 302)

        submission.refresh_from_db()
        self.assertEqual(submission.status, "published")
        self.assertEqual(submission.editorial_decisions.count(), 1)
        article = Article.objects.filter(submission=submission).first()
        self.assertIsNotNone(article)
        self.assertEqual(article.status, "published")

    def test_submission_author_form_validation(self):
        """Проверка, что нельзя добавить дублирующего/второго корреспондирующего автора."""
        submission = Submission.objects.create(
            section=self.section,
            title_ru="Пилотное исследование",
            abstract_ru="Аннотация",
            keywords_ru="ключевые слова",
            language="ru",
            manuscript_file=self._create_manuscript(),
            corresponding_author=self.author,
            status="draft",
        )
        SubmissionAuthor.objects.create(
            submission=submission,
            author=self.author,
            author_order=1,
            is_corresponding=True,
            is_principal=True,
            email=self.author.email,
        )

        # Попытка добавить того же автора повторно
        duplicate_form = SubmissionAuthorForm(
            data={
                "author": self.author.pk,
                "author_order": 2,
                "is_corresponding": False,
                "is_principal": False,
                "affiliation": "",
                "orcid": "",
                "email": "",
            },
            submission=submission,
        )
        self.assertFalse(duplicate_form.is_valid())
        self.assertIn("author", duplicate_form.errors)

        # Попытка добавить нового корреспондирующего автора при уже существующем
        new_author = User.objects.create_user(
            username="new-author",
            password="pass",
            role="author",
            email="new@example.com",
        )
        corr_form = SubmissionAuthorForm(
            data={
                "author": new_author.pk,
                "author_order": 2,
                "is_corresponding": True,
                "is_principal": False,
                "affiliation": "",
                "orcid": "",
                "email": "new@example.com",
            },
            submission=submission,
        )
        self.assertFalse(corr_form.is_valid())
        self.assertIn("is_corresponding", corr_form.errors)
