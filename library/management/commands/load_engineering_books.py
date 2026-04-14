from django.core.management.base import BaseCommand
from library.models import Book


SAMPLE_BOOKS = [
    # title, author, dept, year, sem, isbn, copies
    ("Introduction to Programming", "John Doe", "CSE", 1, 1, "9780000000011", 5),
    ("Data Structures", "Jane Smith", "CSE", 2, 3, "9780000000012", 3),
    ("Digital Electronics", "A. Kumar", "ECE", 1, 2, "9780000000021", 4),
    ("Signals and Systems", "B. Gupta", "ECE", 2, 3, "9780000000022", 2),
    ("Thermodynamics", "C. Rao", "ME", 1, 2, "9780000000031", 2),
    ("Fluid Mechanics", "D. Iyer", "ME", 2, 4, "9780000000032", 2),
    ("Strength of Materials", "E. Singh", "CIVIL", 2, 3, "9780000000041", 3),
    ("Surveying", "F. Sharma", "CIVIL", 3, 5, "9780000000042", 2),

    # SPPU-aligned First Year — Semester I
    ("Engineering Mathematics – I", "SPPU Board", "CSE", 1, 1, "9781000000101", 10),
    ("Engineering Physics – I", "SPPU Board", "CSE", 1, 1, "9781000000102", 10),
    ("Engineering Chemistry – I", "SPPU Board", "CSE", 1, 1, "9781000000103", 10),
    ("Basic Electrical and Electronics Engineering", "SPPU Board", "CSE", 1, 1, "9781000000104", 8),
    ("Engineering Graphics / Drawing", "SPPU Board", "CSE", 1, 1, "9781000000105", 8),
    ("Workshop and Basic Engineering Practices", "SPPU Board", "CSE", 1, 1, "9781000000106", 8),
    ("Human Values and Foundation Course", "SPPU Board", "CSE", 1, 1, "9781000000107", 8),

    # SPPU-aligned First Year — Semester II
    ("Engineering Mathematics – II", "SPPU Board", "CSE", 1, 2, "9781000000201", 10),
    ("Applied Chemistry and Environmental Science", "SPPU Board", "CSE", 1, 2, "9781000000202", 8),
    ("Basic Thermodynamics and Mechanics", "SPPU Board", "CSE", 1, 2, "9781000000203", 8),
    ("Basic Programming and Engineering Computing", "SPPU Board", "CSE", 1, 2, "9781000000204", 12),
    ("Communication Skills and Laboratory", "SPPU Board", "CSE", 1, 2, "9781000000205", 8),
    ("Workshop and Laboratory Practicals II", "SPPU Board", "CSE", 1, 2, "9781000000206", 8),

    # Second Year — Semester III (SE)
    ("Data Structures", "SPPU Board", "CSE", 2, 3, "9781000000301", 12),
    ("Object Oriented Programming and Computer Graphics", "SPPU Board", "CSE", 2, 3, "9781000000302", 10),
    ("Digital Electronics and Logic Design", "SPPU Board", "CSE", 2, 3, "9781000000303", 10),
    ("Operating Systems Fundamentals", "SPPU Board", "CSE", 2, 3, "9781000000304", 10),
    ("Discrete Mathematics for Computer Science", "SPPU Board", "CSE", 2, 3, "9781000000305", 10),

    # Second Year — Semester IV
    ("Database Management Systems", "SPPU Board", "CSE", 2, 4, "9781000000401", 12),
    ("Theory of Computation / Automata", "SPPU Board", "CSE", 2, 4, "9781000000402", 8),
    ("Computer Networks Fundamentals", "SPPU Board", "CSE", 2, 4, "9781000000403", 10),
    ("Software Laboratory Practice IV", "SPPU Board", "CSE", 2, 4, "9781000000404", 8),

    # Third Year — Semester V (TE)
    ("Systems Programming and Operating Systems", "SPPU Board", "CSE", 3, 5, "9781000000501", 10),
    ("Compiler Concepts and Theory of Computation", "SPPU Board", "CSE", 3, 5, "9781000000502", 8),
    ("Advanced Database Management Systems", "SPPU Board", "CSE", 3, 5, "9781000000503", 8),
    ("Elective A: Introduction to Data Science and ML", "SPPU Board", "CSE", 3, 5, "9781000000504", 6),
    ("Technical Communication and Seminar V", "SPPU Board", "CSE", 3, 5, "9781000000505", 6),

    # Third Year — Semester VI
    ("Software Engineering and Project Management", "SPPU Board", "CSE", 3, 6, "9781000000601", 10),
    ("Distributed Systems and Web Technologies", "SPPU Board", "CSE", 3, 6, "9781000000602", 8),
    ("Domain Elective: Network Security", "SPPU Board", "CSE", 3, 6, "9781000000603", 6),
    ("Domain Elective: Artificial Intelligence", "SPPU Board", "CSE", 3, 6, "9781000000604", 6),
    ("Laboratory Practice VI and Project Stage I", "SPPU Board", "CSE", 3, 6, "9781000000605", 6),

    # Fourth Year — Semester VII (BE)
    ("Elective I: Machine Learning", "SPPU Board", "CSE", 4, 7, "9781000000701", 6),
    ("Elective II: Cloud and Mobile Computing", "SPPU Board", "CSE", 4, 7, "9781000000702", 6),
    ("Interdisciplinary Open Elective", "SPPU Board", "CSE", 4, 7, "9781000000703", 6),
    ("Laboratory Practice VII and Project Stage II", "SPPU Board", "CSE", 4, 7, "9781000000704", 6),

    # Fourth Year — Semester VIII
    ("Professional Electives and Open Electives", "SPPU Board", "CSE", 4, 8, "9781000000801", 6),
    ("Project Work Stage II and Viva", "SPPU Board", "CSE", 4, 8, "9781000000802", 6),
    ("Industrial Training and Audit Courses", "SPPU Board", "CSE", 4, 8, "9781000000803", 6),
]


class Command(BaseCommand):
    help = "Load sample engineering books into the database"

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for title, author, dept, year, sem, isbn, copies in SAMPLE_BOOKS:
            obj, was_created = Book.objects.get_or_create(
                isbn=isbn,
                defaults={
                    'title': title,
                    'author': author,
                    'department': dept,
                    'year': year,
                    'semester': sem,
                    'available_copies': copies,
                    'content_url': 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf',
                }
            )
            if was_created:
                created += 1
            else:
                # Backfill content_url if no readable content is present
                if not obj.content_file and not obj.content_url:
                    obj.content_url = 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'
                    updated += 1
                # Keep basic fields in sync with the sample data
                changed = False
                for field, value in {
                    'title': title,
                    'author': author,
                    'department': dept,
                    'year': year,
                    'semester': sem,
                    'available_copies': copies,
                }.items():
                    if getattr(obj, field) != value:
                        setattr(obj, field, value)
                        changed = True
                if changed or updated:
                    obj.save()
        self.stdout.write(self.style.SUCCESS(
            f"Loaded books. Created: {created}, Updated: {updated}, Existing: {len(SAMPLE_BOOKS) - created}"
        ))


