from typing import List, Set
from sqlalchemy.orm import Session
from app.db.models import File, CommitFile, Commit
from app.schemas.impact import ImpactAnalysisResponse, AffectedComponent
from app.services.diff_service import DiffParser

class ImpactService:
    def __init__(self, db: Session, repo_id: int):
        self.db = db
        self.repo_id = repo_id

    def analyze_impact(self, diff_text: str = None, explicit_files: List[str] = None) -> ImpactAnalysisResponse:
        target_files: Set[str] = set()
        if explicit_files:
            target_files.update([f.strip() for f in explicit_files if f.strip()])
        if diff_text:
            target_files.update(DiffParser.extract_changed_files_from_diff(diff_text))

        if not target_files:
            return ImpactAnalysisResponse(
                directly_modified_files=[],
                affected_components=[],
                suggested_tests=[],
                summary="Impact cannot be determined reliably from the available project history. No changed files supplied."
            )

        affected: List[AffectedComponent] = []
        suggested_tests: Set[str] = set()

        for file_path in target_files:
            clean_path = file_path.strip().replace("\\", "/").lstrip("/")
            file_name = clean_path.split("/")[-1]

            # Directly Modified File
            affected.append(AffectedComponent(
                component_name=clean_path,
                impact_category="Direct",
                impact_level="HIGH",
                reason="File is directly included in the submitted change payload.",
                relationship_type="DIRECT_MODIFICATION",
                classification="CONFIRMED",
                supporting_evidence=["Direct file in diff/input"]
            ))

            # Query database using path matching
            db_file = self.db.query(File).filter(
                File.repository_id == self.repo_id,
                (File.path == clean_path) | (File.path.ilike(f"%{file_name}"))
            ).first()

            if not db_file:
                affected.append(AffectedComponent(
                    component_name=clean_path,
                    impact_category="Potential",
                    impact_level="MEDIUM",
                    reason="Newly introduced or untracked file. No prior historical records exist for this path in this repository.",
                    relationship_type="NEW_FILE",
                    classification="INFERRED",
                    supporting_evidence=["Not found in repository history"]
                ))
                continue

            # Historical Author Reviewers
            authors = (
                self.db.query(Commit.author)
                .join(CommitFile, Commit.id == CommitFile.commit_id)
                .filter(CommitFile.file_id == db_file.id)
                .distinct()
                .all()
            )
            author_names = [a[0] for a in authors if a[0]]
            if author_names:
                affected.append(AffectedComponent(
                    component_name=f"Key Reviewers ({', '.join(author_names[:3])})",
                    impact_category="Recorded relationship",
                    impact_level="MEDIUM",
                    reason=f"Historical authors of '{db_file.path}'. Review is recommended to preserve institutional context.",
                    relationship_type="AUTHOR_EXPERTISE",
                    classification="CONFIRMED",
                    supporting_evidence=[f"{len(author_names)} recorded contributor(s)"]
                ))

            # Historical Co-Change Dependencies
            commit_ids = [cf.commit_id for cf in db_file.commit_files]
            if commit_ids:
                co_changed = (
                    self.db.query(File.path, Commit.sha, Commit.message)
                    .join(CommitFile, File.id == CommitFile.file_id)
                    .join(Commit, CommitFile.commit_id == Commit.id)
                    .filter(
                        CommitFile.commit_id.in_(commit_ids),
                        File.id != db_file.id
                    )
                    .limit(6)
                    .all()
                )
                for sib_path, c_sha, c_msg in co_changed:
                    is_test = "test" in sib_path.lower()
                    if is_test:
                        suggested_tests.add(sib_path)

                    affected.append(AffectedComponent(
                        component_name=sib_path,
                        impact_category="Inferred test" if is_test else "Recorded co-change",
                        impact_level="HIGH" if is_test else "MEDIUM",
                        reason=f"Historically committed together in commit {c_sha[:7]}: \"{c_msg.strip()[:50]}\"",
                        relationship_type="HISTORICAL_CO_CHANGE",
                        classification="INFERRED",
                        supporting_evidence=[f"Commit {c_sha[:7]}"]
                    ))

            # Test Suite Heuristic
            file_stem = file_name.split(".")[0]
            matching_test = self.db.query(File).filter(
                File.repository_id == self.repo_id,
                File.path.ilike(f"%{file_stem}%"),
                File.path.ilike("%test%")
            ).first()

            if matching_test and matching_test.path not in target_files:
                suggested_tests.add(matching_test.path)
                affected.append(AffectedComponent(
                    component_name=matching_test.path,
                    impact_category="Inferred test",
                    impact_level="HIGH",
                    reason="Matched test suite naming pattern for this module.",
                    relationship_type="TEST_CORRELATION",
                    classification="INFERRED",
                    supporting_evidence=[f"Pattern match: {file_stem}"]
                ))

        summary = (
            f"Blast radius analysis complete: {len(target_files)} direct file(s) modified, "
            f"{len(affected) - len(target_files)} coupled component(s) identified, "
            f"and {len(suggested_tests)} test suite(s) recommended."
        )

        return ImpactAnalysisResponse(
            directly_modified_files=sorted(list(target_files)),
            affected_components=affected,
            suggested_tests=sorted(list(suggested_tests)),
            summary=summary
        )