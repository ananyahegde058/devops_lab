import unittest
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home(self):
        response = self.app.get("/")
        content = response.data.decode("utf-8")
        print(f"\n[TEST LOG] Received response: {content}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, "Hello, Jenkins Multi-Stage Pipeline!")

if __name__ == "__main__":
    unittest.main()
