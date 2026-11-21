import requests


class ApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api"
        self.token = None
        self.user = None

    def _headers(self) -> dict:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _handle_response(self, resp: requests.Response):
        try:
            data = resp.json()
        except ValueError:
            data = {}
        if not resp.ok:
            raise RuntimeError(data.get("detail", f"Request failed ({resp.status_code})"))
        return data

    # --- Auth ---
    def login(self, email: str, password: str) -> dict:
        resp = requests.post(
            f"{self.api_url}/auth/login",
            json={"email": email, "password": password},
            timeout=10,
        )
        data = self._handle_response(resp)
        user = data.get("user", {})
        if user.get("role") == "citizen":
            raise RuntimeError("Citizen accounts cannot access the Municipal Admin Console.")
        self.token = data["access_token"]
        self.user = user
        return data

    def admin_register(self, name: str, email: str, password: str) -> dict:
        resp = requests.post(
            f"{self.api_url}/auth/admin-register",
            json={"name": name, "email": email, "password": password},
            timeout=10,
        )
        return self._handle_response(resp)

    def logout(self):
        self.token = None
        self.user = None

    # --- Complaints & Triage ---
    def get_complaints(self, category_id=None, status=None) -> list:
        params = {}
        if category_id and category_id != "all":
            params["category_id"] = category_id
        if status and status != "all":
            params["status"] = status
        resp = requests.get(
            f"{self.api_url}/complaints",
            headers=self._headers(),
            params=params,
            timeout=10,
        )
        return self._handle_response(resp)

    def get_complaint(self, complaint_id: int) -> dict:
        resp = requests.get(
            f"{self.api_url}/complaints/{complaint_id}",
            headers=self._headers(),
            timeout=10,
        )
        return self._handle_response(resp)

    def update_status(
        self,
        complaint_id: int,
        status: str,
        department_id: int = None,
        note: str = None,
        rejection_reason: str = None,
    ) -> dict:
        payload = {"status": status}
        if department_id is not None:
            payload["department_id"] = department_id
        if note:
            payload["note"] = note
        if rejection_reason:
            payload["rejection_reason"] = rejection_reason

        resp = requests.patch(
            f"{self.api_url}/complaints/{complaint_id}/status",
            headers=self._headers(),
            json=payload,
            timeout=10,
        )
        return self._handle_response(resp)

    def upload_resolution_photo(self, complaint_id: int, filepath: str) -> dict:
        with open(filepath, "rb") as f:
            files = {"photo": (filepath.split("/")[-1], f, "image/jpeg")}
            resp = requests.post(
                f"{self.api_url}/admin/complaints/{complaint_id}/resolution-photo",
                headers=self._headers(),
                files=files,
                timeout=20,
            )
        return self._handle_response(resp)

    # --- Departments ---
    def get_departments(self) -> list:
        resp = requests.get(
            f"{self.api_url}/admin/departments",
            headers=self._headers(),
            timeout=10,
        )
        return self._handle_response(resp)

    # --- Duplicates ---
    def get_pending_duplicates(self) -> list:
        resp = requests.get(
            f"{self.api_url}/admin/duplicates",
            headers=self._headers(),
            timeout=10,
        )
        return self._handle_response(resp)

    def decide_duplicate(self, review_id: int, decision: str) -> dict:
        resp = requests.post(
            f"{self.api_url}/admin/duplicates/{review_id}/decide",
            headers=self._headers(),
            json={"decision": decision},
            timeout=10,
        )
        return self._handle_response(resp)

    # --- Analytics ---
    def get_analytics(self) -> dict:
        resp = requests.get(
            f"{self.api_url}/analytics",
            headers=self._headers(),
            timeout=10,
        )
        return self._handle_response(resp)

    # --- Manager / Role Management ---
    def get_invites(self) -> list:
        resp = requests.get(
            f"{self.api_url}/admin/invites",
            headers=self._headers(),
            timeout=10,
        )
        return self._handle_response(resp)

    def create_invite(self, email: str, role: str, department_id: int = None) -> dict:
        payload = {"email": email, "role": role}
        if department_id is not None:
            payload["department_id"] = department_id
        resp = requests.post(
            f"{self.api_url}/admin/invites",
            headers=self._headers(),
            json=payload,
            timeout=10,
        )
        return self._handle_response(resp)

    def get_users(self) -> list:
        resp = requests.get(
            f"{self.api_url}/admin/users",
            headers=self._headers(),
            timeout=10,
        )
        return self._handle_response(resp)

    def update_user_role(self, user_id: int, role: str) -> dict:
        resp = requests.patch(
            f"{self.api_url}/admin/users/{user_id}/role",
            headers=self._headers(),
            params={"role": role},
            timeout=10,
        )
        return self._handle_response(resp)