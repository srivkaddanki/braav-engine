from supabase import create_client, Client

class OrbBridge:
    def __init__(self, url: str, key: str):
        # The connection to the Satellite (Supabase)
        self.db: Client = create_client(url, key)

    def log_thought(self, content: str, project_id: str = None, todo_id: str = None):
        """Standard Thought Log"""
        data = {
            "content": content,
            "project_id": project_id,
            "todo_id": todo_id
        }
        return self.db.table("thoughts").insert(data).execute()

    def create_project(self, name: str):
        """The '+' Command"""
        return self.db.table("projects").insert({"name": name}).execute()

    def get_top_projects(self):
        """The Ribbon Sync"""
        res = self.db.table("projects").select("id, name").order("created_at", desc=True).limit(3).execute()
        return res.data # Returns a list of dicts: [{'id': '...', 'name': '...'}, ...]