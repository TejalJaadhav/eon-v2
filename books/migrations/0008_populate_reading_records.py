from django.db import migrations


def populate_reading_records(apps, schema_editor):
    Book = apps.get_model("books", "Book")
    ReadingRecord = apps.get_model("books", "ReadingRecord")
    database = schema_editor.connection.alias

    books = Book.objects.using(database).filter(
        status__in=["currently_reading", "read"]
    )

    for book in books.iterator():
        records = ReadingRecord.objects.using(database)

        if records.filter(book_id=book.pk).exists():
            continue

        records.create(
            book_id=book.pk,
            current_page=book.current_page,
            total_pages=book.total_pages,
            started_at=book.started_at,
            finished_at=book.finished_at,
            is_finished=book.status == "read",
        )


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0007_readingrecord"),
    ]

    operations = [
        migrations.RunPython(populate_reading_records),
    ]