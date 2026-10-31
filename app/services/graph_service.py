"""
Builds the deterministic NetworkX knowledge graph from stored records.

Maintains strict separation between:
1. Database-imported entities (Issues, PRs, Commits, Files, Authors)
2. Referenced-only entities created from relationship records (e.g. issues or PRs
   referenced in commit messages/PR descriptions that fall outside the fetched batch).

Exposes distinct metrics for imported GitHub issues, referenced issue nodes,
and total graph issue nodes.
"""

import networkx as nx
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.db.models import Commit, File, CommitFile, Issue, PullRequest, RelationshipRecord


def node_id(entity_type: str, identifier) -> str:
    """Single source of truth for node ids — must be used everywhere a
    node is created OR looked up, including when building ids from
    RelationshipRecord rows."""
    return f"{entity_type.lower()}:{identifier}"


def _pretty_label(entity_type: str, identifier) -> str:
    s = str(identifier)
    if entity_type == "Commit":
        return s[:7]
    if entity_type == "Issue":
        return f"#{s}"
    if entity_type == "PullRequest":
        return f"PR #{s}"
    return s


def _pretty_title(entity_type: str, identifier) -> str:
    s = str(identifier)
    if entity_type == "Author":
        return f"Author: {s}"
    if entity_type == "Commit":
        return f"Commit: {s}"
    if entity_type == "File":
        return f"File: {s}"
    if entity_type == "Issue":
        return f"Issue #{s} (Referenced in git history / PRs — outside imported batch)"
    if entity_type == "PullRequest":
        return f"PR #{s} (Referenced in git history — outside imported batch)"
    return s


class GraphService:
    def __init__(self, db: Session, repo_id: int):
        self.db = db
        self.repo_id = repo_id

    def build_networkx_graph(self) -> nx.DiGraph:
        G = nx.DiGraph()

        # Commits & Authors
        commits = self.db.query(Commit).filter(Commit.repository_id == self.repo_id).all()
        for c in commits:
            commit_node = node_id("Commit", c.sha)
            author_node = node_id("Author", c.author)
            G.add_node(
                commit_node,
                type="Commit",
                label=c.sha[:7],
                title=f"Commit: {c.message[:70]}",
                url=c.source_url,
                is_imported=True,
                is_referenced=False,
                origin="database"
            )
            G.add_node(
                author_node,
                type="Author",
                label=c.author,
                title=f"Author: {c.author}",
                is_imported=True,
                is_referenced=False,
                origin="database"
            )
            G.add_edge(
                author_node,
                commit_node,
                rel="AUTHORED",
                provenance="Git metadata",
                classification="CONFIRMED"
            )

        # Files & Commit -> File
        commit_files = (
            self.db.query(CommitFile, Commit.sha, File.path)
            .join(Commit, CommitFile.commit_id == Commit.id)
            .join(File, CommitFile.file_id == File.id)
            .filter(Commit.repository_id == self.repo_id)
            .all()
        )
        for _, sha, path in commit_files:
            file_node = node_id("File", path)
            G.add_node(
                file_node,
                type="File",
                label=path.split("/")[-1],
                title=f"File: {path}",
                full_path=path,
                is_imported=True,
                is_referenced=False,
                origin="database"
            )
            G.add_edge(
                node_id("Commit", sha),
                file_node,
                rel="MODIFIES",
                provenance="Commit diff",
                classification="CONFIRMED"
            )

        # Issues
        issues = self.db.query(Issue).filter(Issue.repository_id == self.repo_id).all()
        for iss in issues:
            iss_node = node_id("Issue", iss.issue_number)
            G.add_node(
                iss_node,
                type="Issue",
                label=f"#{iss.issue_number}",
                title=f"Issue #{iss.issue_number}: {iss.title}",
                url=iss.source_url,
                is_imported=True,
                is_referenced=False,
                origin="database"
            )

        # Pull Requests
        prs = self.db.query(PullRequest).filter(PullRequest.repository_id == self.repo_id).all()
        for pr in prs:
            pr_node = node_id("PullRequest", pr.pr_number)
            G.add_node(
                pr_node,
                type="PullRequest",
                label=f"PR #{pr.pr_number}",
                title=f"PR #{pr.pr_number}: {pr.title}",
                url=pr.source_url,
                is_imported=True,
                is_referenced=False,
                origin="database"
            )

        # Relationship records
        known_pr_nums = {str(pr.pr_number) for pr in prs}

        relationships = self.db.query(RelationshipRecord).filter(
            RelationshipRecord.repository_id == self.repo_id
        ).all()

        for r in relationships:
            src_type = r.source_type
            src_id = r.source_id
            tgt_type = r.target_type
            tgt_id = r.target_id

            if tgt_type == "Issue" and str(tgt_id) in known_pr_nums:
                tgt_type = "PullRequest"
            if src_type == "Issue" and str(src_id) in known_pr_nums:
                src_type = "PullRequest"

            src = node_id(src_type, src_id)
            tgt = node_id(tgt_type, tgt_id)

            if not G.has_node(src):
                G.add_node(
                    src,
                    type=src_type,
                    label=_pretty_label(src_type, src_id),
                    title=_pretty_title(src_type, src_id),
                    is_imported=False,
                    is_referenced=True,
                    origin="referenced"
                )
            if not G.has_node(tgt):
                G.add_node(
                    tgt,
                    type=tgt_type,
                    label=_pretty_label(tgt_type, tgt_id),
                    title=_pretty_title(tgt_type, tgt_id),
                    is_imported=False,
                    is_referenced=True,
                    origin="referenced"
                )

            G.add_edge(
                src,
                tgt,
                rel=r.relationship_type,
                provenance=r.provenance,
                classification=r.classification
            )

        # Deterministic test-file pairing
        self._attach_code_and_test_edges(G)

        # Deterministic issue & PR delivery memory anchoring
        self._attach_issue_and_pr_anchors(G)

        return G

    def _attach_issue_and_pr_anchors(self, G: nx.DiGraph):
        """
        Ensures issues and pull requests are properly connected to the delivery graph
        so they remain visible, interactive, and correctly clustered around the project core.
        """
        files = [n for n, d in G.nodes(data=True) if d.get("type") == "File"]
        readme_files = [f for f in files if "readme" in f.lower()]
        primary_core = readme_files[0] if readme_files else (files[0] if files else None)

        if not primary_core:
            commits = [n for n, d in G.nodes(data=True) if d.get("type") == "Commit"]
            if commits:
                primary_core = max(commits, key=lambda c: G.degree(c))

        # Anchor Issues
        issue_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "Issue"]
        for iss in issue_nodes:
            # Check title mentions of known repo files
            iss_title = (G.nodes[iss].get("title") or "").lower()
            for f in files:
                f_label = (G.nodes[f].get("label") or "").lower()
                if len(f_label) > 3 and f_label in iss_title:
                    if not G.has_edge(iss, f) and not G.has_edge(f, iss):
                        G.add_edge(
                            iss,
                            f,
                            rel="REFERENCES_FILE",
                            provenance="Issue title reference",
                            classification="CONFIRMED"
                        )

            edges = list(G.edges(iss)) + list(G.in_edges(iss))
            has_proj_link = any(
                G.nodes[e[0] if e[1] == iss else e[1]].get("type") in ("File", "Commit", "PullRequest")
                for e in edges
            )
            if not has_proj_link and primary_core:
                G.add_edge(
                    primary_core,
                    iss,
                    rel="TRACKS_ISSUE",
                    provenance="Repository issue tracker",
                    classification="CONFIRMED"
                )

        # Anchor Pull Requests that have no commit/file connection
        pr_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "PullRequest"]
        for pr in pr_nodes:
            edges = list(G.edges(pr)) + list(G.in_edges(pr))
            has_proj_link = any(
                G.nodes[e[0] if e[1] == pr else e[1]].get("type") in ("File", "Commit", "Issue")
                for e in edges
            )
            if not has_proj_link and primary_core:
                G.add_edge(
                    pr,
                    primary_core,
                    rel="PROPOSED_IN",
                    provenance="Repository pull request tracker",
                    classification="CONFIRMED"
                )

    def _attach_code_and_test_edges(self, G: nx.DiGraph):
        files = [n for n, d in G.nodes(data=True) if d.get("type") == "File"]
        test_files = [f for f in files if "test" in f.lower()]
        source_files = [f for f in files if "test" not in f.lower()]

        for tf in test_files:
            tf_clean = tf.replace("file:", "").split("/")[-1]
            tf_stem = tf_clean.replace("test_", "").replace("_test", "").split(".")[0]
            if len(tf_stem) > 2:
                for sf in source_files:
                    sf_clean = sf.replace("file:", "").split("/")[-1]
                    sf_stem = sf_clean.split(".")[0]
                    if tf_stem == sf_stem:
                        G.add_edge(
                            sf,
                            tf,
                            rel="TESTED_BY",
                            provenance="Deterministic naming convention",
                            classification="INFERRED"
                        )

    def audit_graph_integrity(self) -> Dict[str, Any]:
        G = self.build_networkx_graph()
        isolated_nodes = list(nx.isolates(G))
        audit_details = []

        imported_issues = [n for n, d in G.nodes(data=True) if d.get("type") == "Issue" and d.get("is_imported")]
        referenced_issues = [n for n, d in G.nodes(data=True) if d.get("type") == "Issue" and d.get("is_referenced")]
        total_issues = [n for n, d in G.nodes(data=True) if d.get("type") == "Issue"]

        imported_prs = [n for n, d in G.nodes(data=True) if d.get("type") == "PullRequest" and d.get("is_imported")]
        referenced_prs = [n for n, d in G.nodes(data=True) if d.get("type") == "PullRequest" and d.get("is_referenced")]
        total_prs = [n for n, d in G.nodes(data=True) if d.get("type") == "PullRequest"]

        db_issues_count = self.db.query(Issue).filter(Issue.repository_id == self.repo_id).count()
        db_prs_count = self.db.query(PullRequest).filter(PullRequest.repository_id == self.repo_id).count()
        db_rels_count = self.db.query(RelationshipRecord).filter(RelationshipRecord.repository_id == self.repo_id).count()

        for node in isolated_nodes:
            data = G.nodes[node]
            node_type = data.get("type")
            label = data.get("label")
            reason = "Node exists in records, but its related commit or issue falls outside the fetched batch window."
            if node_type == "PullRequest":
                reason = "PR has no commits or issue references within the analyzed commit history."
            elif node_type == "File":
                reason = "File was imported via reference without commit details attached."
            elif node_type == "Issue":
                reason = "No commit or PR in the current batch mentions this issue number."

            audit_details.append({
                "node_id": node, "type": node_type, "label": label, "reason": reason
            })

        return {
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "connected_components": nx.number_weakly_connected_components(G),
            "isolated_count": len(isolated_nodes),
            "isolated_nodes": audit_details,
            "database_issues_count": db_issues_count,
            "imported_issues_count": len(imported_issues),
            "referenced_issues_count": len(referenced_issues),
            "total_graph_issues_count": len(total_issues),
            "database_prs_count": db_prs_count,
            "imported_prs_count": len(imported_prs),
            "referenced_prs_count": len(referenced_prs),
            "total_graph_prs_count": len(total_prs),
            "relationships_count": db_rels_count,
        }

    def get_graph_export(self) -> dict:
        G = self.build_networkx_graph()
        audit = self.audit_graph_integrity()
        nodes = [
            {
                "id": n,
                "label": data.get("label", n),
                "group": data.get("type", "Unknown"),
                "title": data.get("title") or n,
                "is_imported": data.get("is_imported", False),
                "is_referenced": data.get("is_referenced", False),
                "origin": data.get("origin", "inferred" if data.get("is_referenced") else "database")
            }
            for n, data in G.nodes(data=True)
        ]
        edges = [
            {
                "from": u,
                "to": v,
                "title": f"[{data.get('rel', 'CONNECTED_TO')}] Provenance: {data.get('provenance', 'N/A')}",
                "classification": data.get("classification", "CONFIRMED")
            }
            for u, v, data in G.edges(data=True)
        ]
        return {
            "nodes": nodes,
            "edges": edges,
            "audit": audit,
            "metrics": {
                "imported_issues_count": audit["imported_issues_count"],
                "referenced_issues_count": audit["referenced_issues_count"],
                "total_graph_issues_count": audit["total_graph_issues_count"],
                "imported_prs_count": audit["imported_prs_count"],
                "referenced_prs_count": audit["referenced_prs_count"],
                "total_graph_prs_count": audit["total_graph_prs_count"],
                "database_issues_count": audit["database_issues_count"],
            }
        }
