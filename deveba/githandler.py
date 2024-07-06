from deveba.gitrepo import GitRepo
from deveba import utils
from deveba.handler import Handler


class GitHandler(Handler):
    __slots__ = ["repo"]

    def __init__(self, repo_path):
        Handler.__init__(self)
        self.repo = GitRepo(repo_path)

    @classmethod
    def create(cls, repo_path, options):
        if not (repo_path / ".git").exists():
            return None
        return GitHandler(repo_path)

    def __str__(self):
        return f"git: {self.repo.path}"

    def sync(self, ui):
        def format_list(lst):
            return "\n".join("- " + x for x in lst)

        status = self.repo.get_status()

        if status.has_changes():
            while True:
                modified_str = format_list(status.modified_files)
                new_str = format_list(status.new_files)
                ui.log_verbose(
                    f"Modified files:\n{modified_str}\n\nNew files:\n{new_str}\n"
                )
                choices = ["Commit", "Show Diff"]
                answer = ui.question("Uncommitted changes detected", choices, "Commit")
                if answer == "Commit":
                    ui.log_info("Committing changes")
                    self._commit(status.new_files)
                    break
                elif answer == "Show Diff":
                    ui.log_verbose(self.repo.run_git("diff"))
                elif answer == ui.CANCEL:
                    ui.log_warning("Cancelled commit")
                    break

        self.repo.run_git("fetch")

        if self.repo.need_merge():
            if not ui.confirm("Upstream changes fetched, merge them?", True):
                ui.log_warning("Cancelled merge")
                return
            ui.log_info("Merging upstream changes")
            self.repo.merge("origin/master")

        if self.repo.need_push():
            if not ui.confirm("Local changes not pushed, push them?", True):
                ui.log_warning("Cancelled push")
                return
            ui.log_info("Pushing changes")
            self.repo.run_git("push")

    def _commit(self, new_files):
        if len(new_files) > 0:
            self.repo.add(*new_files)

        msg = utils.generate_commit_message(self.group)
        name = utils.get_commit_author_name()
        email = utils.get_commit_author_email()
        author = f"{name} <{email}>"
        self.repo.commit(msg, "-a", "--author", author)
