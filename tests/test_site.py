import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_SLUGS = {
    "where-i-want-to-be",
    "the-making-of-whereis-co",
    "it-is-about-the-bike",
    "relating-happiness-and-money",
    "i-fucked-up",
    "being-over-your-head",
}


class SiteTests(unittest.TestCase):
    def test_complete_archive_is_present(self):
        actual = {
            path.parent.name
            for path in (ROOT / "writing").glob("*/index.html")
        }
        self.assertEqual(ARTICLE_SLUGS, actual)

    def test_pages_have_unique_canonical_and_no_import_artifacts(self):
        canonicals = set()
        for slug in ARTICLE_SLUGS:
            markup = (ROOT / "writing" / slug / "index.html").read_text()
            self.assertIn("<article", markup)
            self.assertNotIn("Originally published on", markup)
            self.assertNotIn('class="tags"', markup)
            match = re.search(r'<link rel="canonical" href="([^"]+)">', markup)
            self.assertIsNotNone(match)
            canonicals.add(match.group(1))
        self.assertEqual(len(ARTICLE_SLUGS), len(canonicals))

    def test_imported_images_are_local_and_exist(self):
        markup = "\n".join(
            path.read_text()
            for path in (ROOT / "writing").glob("*/index.html")
        )
        sources = re.findall(r'<img[^>]+src="(/writing/assets/[^"]+)"', markup)
        self.assertEqual(3, len(sources))
        for source in sources:
            self.assertTrue((ROOT / source.lstrip("/")).is_file(), source)

    def test_navigation_points_to_local_archive(self):
        home = (ROOT / "index.html").read_text()
        self.assertIn("href='/writing/'", home)

    def test_reading_progress_is_limited_to_articles(self):
        archive = (ROOT / "writing" / "index.html").read_text()
        self.assertNotIn("data-reading-progress", archive)
        self.assertNotIn("reading-progress.js", archive)

        for slug in ARTICLE_SLUGS:
            markup = (ROOT / "writing" / slug / "index.html").read_text()
            self.assertIn('data-reading-progress role="progressbar"', markup)
            self.assertIn('aria-valuemin="0"', markup)
            self.assertIn('aria-valuemax="100"', markup)
            self.assertIn(
                '<script src="/writing/reading-progress.js?v=20260823a"></script>',
                markup,
            )

    def test_local_links_and_assets_resolve(self):
        pages = [ROOT / "index.html", ROOT / "writing" / "index.html"]
        pages.extend((ROOT / "writing").glob("*/index.html"))
        for page in pages:
            markup = page.read_text()
            references = re.findall(r'(?:href|src)=["\'](/[^"\']+)', markup)
            for reference in references:
                path = reference.split("?", 1)[0].split("#", 1)[0]
                target = ROOT / path.lstrip("/")
                if path.endswith("/"):
                    target /= "index.html"
                self.assertTrue(target.exists(), f"{page}: {reference}")

    def test_xml_documents_are_valid_and_complete(self):
        ET.parse(ROOT / "sitemap.xml")
        feed = ET.parse(ROOT / "writing" / "feed.xml")
        self.assertEqual(6, len(feed.findall("./channel/item")))
        sitemap = (ROOT / "sitemap.xml").read_text()
        for slug in ARTICLE_SLUGS:
            self.assertIn(f"/writing/{slug}/", sitemap)


if __name__ == "__main__":
    unittest.main()
