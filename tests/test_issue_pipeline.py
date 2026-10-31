import unittest
import asyncio
from unittest.mock import patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import Repository, Commit, File, CommitFile, Issue, PullRequest, RelationshipRecord
from app.services.import_service import ImportService
from app.services.graph_service import GraphService
from app.utils.text_normalization import extract_issue_numbers, extract_pr_numbers
from app.collectors.github_collector import GitHubCollector


class TestIssuePipeline(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        self.repo1 = Repository(owner="testowner", name="repo1", url="https://github.com/testowner/repo1", import_status="COMPLETED")
        self.repo2 = Repository(owner="testowner", name="repo2", url="https://github.com/testowner/repo2", import_status="COMPLETED")
        self.db.add_all([self.repo1, self.repo2])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_1_importing_same_issue_twice_does_not_create_duplicates(self):
        """Test 1: Importing the same issue twice does not create duplicates."""
        service = ImportService(self.db)
        fake_issues = [
            {"issue_number": 42, "title": "Initial Title", "description": "Initial Desc", "author": "dev1", "state": "open", "source_url": "http://gh/42"},
        ]

        with patch.object(GitHubCollector, "fetch_commits", new_callable=AsyncMock, return_value=[]), \
             patch.object(GitHubCollector, "fetch_pull_requests", new_callable=AsyncMock, return_value=[]), \
             patch.object(GitHubCollector, "fetch_issues", new_callable=AsyncMock, return_value=fake_issues):
            asyncio.run(service.import_repository("https://github.com/testowner/repo1"))

        issues = self.db.query(Issue).filter(Issue.repository_id == self.repo1.id).all()
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].title, "Initial Title")

        fake_issues_updated = [
            {"issue_number": 42, "title": "Updated Title", "description": "Updated Desc", "author": "dev1", "state": "closed", "source_url": "http://gh/42"},
        ]
        with patch.object(GitHubCollector, "fetch_commits", new_callable=AsyncMock, return_value=[]), \
             patch.object(GitHubCollector, "fetch_pull_requests", new_callable=AsyncMock, return_value=[]), \
             patch.object(GitHubCollector, "fetch_issues", new_callable=AsyncMock, return_value=fake_issues_updated):
            asyncio.run(service.import_repository("https://github.com/testowner/repo1"))

        issues_after = self.db.query(Issue).filter(Issue.repository_id == self.repo1.id).all()
        self.assertEqual(len(issues_after), 1)
        self.assertEqual(issues_after[0].title, "Updated Title")
        self.assertEqual(issues_after[0].state, "closed")

    def test_2_two_repositories_can_have_same_issue_number_without_colliding(self):
        """Test 2: Two repositories can have the same issue number without colliding."""
        iss1 = Issue(repository_id=self.repo1.id, issue_number=100, title="Repo 1 Issue", state="open", source_url="http://gh1/100")
        iss2 = Issue(repository_id=self.repo2.id, issue_number=100, title="Repo 2 Issue", state="closed", source_url="http://gh2/100")
        self.db.add_all([iss1, iss2])
        self.db.commit()

        r1_issues = self.db.query(Issue).filter(Issue.repository_id == self.repo1.id).all()
        r2_issues = self.db.query(Issue).filter(Issue.repository_id == self.repo2.id).all()

        self.assertEqual(len(r1_issues), 1)
        self.assertEqual(len(r2_issues), 1)
        self.assertEqual(r1_issues[0].title, "Repo 1 Issue")
        self.assertEqual(r2_issues[0].title, "Repo 2 Issue")

    def test_3_pull_requests_are_not_counted_as_actual_issues(self):
        """Test 3: Pull requests are not counted as actual Issues."""
        service = ImportService(self.db)
        fake_prs = [
            {"pr_number": 201, "title": "Add feature", "description": "PR body", "author": "pr_author", "state": "open", "source_url": "http://gh/pr/201"}
        ]
        fake_issues = [
            {"issue_number": 101, "title": "Real issue", "description": "Issue body", "author": "issue_author", "state": "open", "source_url": "http://gh/issue/101"}
        ]

        with patch.object(GitHubCollector, "fetch_commits", new_callable=AsyncMock, return_value=[]), \
             patch.object(GitHubCollector, "fetch_pull_requests", new_callable=AsyncMock, return_value=fake_prs), \
             patch.object(GitHubCollector, "fetch_issues", new_callable=AsyncMock, return_value=fake_issues):
            asyncio.run(service.import_repository("https://github.com/testowner/repo1"))

        issue_count = self.db.query(Issue).filter(Issue.repository_id == self.repo1.id).count()
        pr_count = self.db.query(PullRequest).filter(PullRequest.repository_id == self.repo1.id).count()

        self.assertEqual(issue_count, 1)
        self.assertEqual(pr_count, 1)
        self.assertIsNone(self.db.query(Issue).filter(Issue.repository_id == self.repo1.id, Issue.issue_number == 201).first())

    def test_4_multiple_github_issue_pages_are_imported(self):
        """Test 4: Multiple GitHub issue pages are imported via collector."""
        collector = GitHubCollector("testowner", "testrepo")
        
        page1_data = [{"number": i, "title": f"Issue {i}", "body": "...", "state": "closed", "html_url": f"http://gh/{i}", "user": {"login": "user1"}} for i in range(1, 26)]
        page2_data = [{"number": i, "title": f"Issue {i}", "body": "...", "state": "closed", "html_url": f"http://gh/{i}", "user": {"login": "user1"}} for i in range(26, 51)]

        async def mock_get(url, params=None):
            resp = unittest.mock.MagicMock()
            resp.status_code = 200
            page = params.get("page", 1) if params else 1
            if "search/issues" in url:
                if page == 1:
                    resp.json.return_value = {"total_count": 50, "items": page1_data}
                elif page == 2:
                    resp.json.return_value = {"total_count": 50, "items": page2_data}
                else:
                    resp.json.return_value = {"total_count": 50, "items": []}
            return resp

        with patch("httpx.AsyncClient.get", side_effect=mock_get):
            issues = asyncio.run(collector.fetch_issues(limit=50))

        self.assertEqual(len(issues), 50)
        self.assertEqual(issues[0]["issue_number"], 1)
        self.assertEqual(issues[49]["issue_number"], 50)

    def test_5_graph_relationship_only_issue_nodes_distinguished_from_imported(self):
        """Test 5: Graph relationship-only issue nodes are distinguished from imported issues."""
        self.db.add(Issue(repository_id=self.repo1.id, issue_number=10, title="Imported Issue", state="open", source_url="http://gh/10"))
        self.db.add(RelationshipRecord(
            repository_id=self.repo1.id,
            source_type="Commit",
            source_id="sha123",
            target_type="Issue",
            target_id="999",
            relationship_type="CLOSES_OR_REFERENCES",
            provenance="Commit issue reference",
            classification="CONFIRMED"
        ))
        self.db.commit()

        graph_service = GraphService(self.db, self.repo1.id)
        G = graph_service.build_networkx_graph()

        node_10 = G.nodes["issue:10"]
        node_999 = G.nodes["issue:999"]

        self.assertTrue(node_10.get("is_imported"))
        self.assertFalse(node_10.get("is_referenced"))
        self.assertEqual(node_10.get("origin"), "database")

        self.assertFalse(node_999.get("is_imported"))
        self.assertTrue(node_999.get("is_referenced"))
        self.assertEqual(node_999.get("origin"), "referenced")

    def test_6_dashboard_counts_match_database_distinct_issue_count(self):
        """Test 6: Dashboard counts match the database's distinct issue count."""
        self.db.add_all([
            Issue(repository_id=self.repo1.id, issue_number=1, title="Iss 1", state="open", source_url="http://gh/1"),
            Issue(repository_id=self.repo1.id, issue_number=2, title="Iss 2", state="closed", source_url="http://gh/2"),
            Issue(repository_id=self.repo1.id, issue_number=3, title="Iss 3", state="closed", source_url="http://gh/3"),
        ])
        self.db.commit()

        from app.api.routes.repositories import get_repository_stats
        stats = get_repository_stats(self.repo1.id, self.db)

        self.assertEqual(stats.issues_count, 3)
        self.assertEqual(stats.distinct_issues_count, 3)
        self.assertEqual(stats.open_issues_count, 1)
        self.assertEqual(stats.closed_issues_count, 2)

    def test_7_graph_count_explainable_by_imported_plus_referenced(self):
        """Test 7: Graph count is explainable by imported plus relationship-only issue nodes."""
        self.db.add(Issue(repository_id=self.repo1.id, issue_number=1, title="Iss 1", state="open", source_url="http://gh/1"))
        self.db.add(Issue(repository_id=self.repo1.id, issue_number=2, title="Iss 2", state="open", source_url="http://gh/2"))
        self.db.add(RelationshipRecord(
            repository_id=self.repo1.id,
            source_type="Commit",
            source_id="sha1",
            target_type="Issue",
            target_id="300",
            relationship_type="CLOSES_OR_REFERENCES",
            provenance="Commit issue reference",
            classification="CONFIRMED"
        ))
        self.db.commit()

        graph_service = GraphService(self.db, self.repo1.id)
        audit = graph_service.audit_graph_integrity()

        self.assertEqual(audit["imported_issues_count"], 2)
        self.assertEqual(audit["referenced_issues_count"], 1)
        self.assertEqual(audit["total_graph_issues_count"], 3)
        self.assertEqual(audit["total_graph_issues_count"], audit["imported_issues_count"] + audit["referenced_issues_count"])

    def test_8_repository_selection_consistency(self):
        """Test 8: Repository selection is strictly scoped by repository_id."""
        self.db.add(Issue(repository_id=self.repo1.id, issue_number=10, title="R1 Issue", state="open", source_url="http://gh/10"))
        self.db.add(Issue(repository_id=self.repo2.id, issue_number=20, title="R2 Issue", state="open", source_url="http://gh/20"))
        self.db.commit()

        g1 = GraphService(self.db, self.repo1.id).build_networkx_graph()
        g2 = GraphService(self.db, self.repo2.id).build_networkx_graph()

        self.assertTrue(g1.has_node("issue:10"))
        self.assertFalse(g1.has_node("issue:20"))

        self.assertTrue(g2.has_node("issue:20"))
        self.assertFalse(g2.has_node("issue:10"))

    def test_9_reimporting_repository_does_not_inflate_issue_counts(self):
        """Test 9: Re-importing a repository does not inflate issue counts."""
        service = ImportService(self.db)
        fake_issues = [
            {"issue_number": 1, "title": "Issue 1", "description": "", "author": "a1", "state": "open", "source_url": "http://gh/1"},
            {"issue_number": 2, "title": "Issue 2", "description": "", "author": "a2", "state": "open", "source_url": "http://gh/2"},
        ]

        for _ in range(3):
            with patch.object(GitHubCollector, "fetch_commits", new_callable=AsyncMock, return_value=[]), \
                 patch.object(GitHubCollector, "fetch_pull_requests", new_callable=AsyncMock, return_value=[]), \
                 patch.object(GitHubCollector, "fetch_issues", new_callable=AsyncMock, return_value=fake_issues):
                asyncio.run(service.import_repository("https://github.com/testowner/repo1"))

        issue_rows = self.db.query(Issue).filter(Issue.repository_id == self.repo1.id).all()
        self.assertEqual(len(issue_rows), 2)

    def test_10_existing_commit_graph_functionality_remains_intact(self):
        """Test 10: Existing commit graph functionality remains intact."""
        commit = Commit(repository_id=self.repo1.id, sha="abc1234567890", message="Test commit", author="alice", source_url="http://gh/commit/abc")
        file1 = File(repository_id=self.repo1.id, path="src/main.py", file_type="py")
        self.db.add_all([commit, file1])
        self.db.flush()

        cf = CommitFile(commit_id=commit.id, file_id=file1.id)
        self.db.add(cf)
        self.db.commit()

        G = GraphService(self.db, self.repo1.id).build_networkx_graph()

        self.assertTrue(G.has_node("commit:abc1234567890"))
        self.assertTrue(G.has_node("author:alice"))
        self.assertTrue(G.has_node("file:src/main.py"))

        # Check edges
        self.assertTrue(G.has_edge("author:alice", "commit:abc1234567890"))
        self.assertTrue(G.has_edge("commit:abc1234567890", "file:src/main.py"))
        self.assertEqual(G["author:alice"]["commit:abc1234567890"]["rel"], "AUTHORED")
        self.assertEqual(G["commit:abc1234567890"]["file:src/main.py"]["rel"], "MODIFIES")


if __name__ == "__main__":
    unittest.main()