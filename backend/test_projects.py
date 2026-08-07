import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
import json
import unittest

class TestProjectsAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        
        # Clear the database for testing
        from models import db, Project
        with cls.app.app_context():
            Project.__table__.drop(db.engine, checkfirst=True)
            Project.__table__.create(db.engine, checkfirst=True)

    def post_project(self, payload):
        return self.client.post('/api/projects', data=json.dumps(payload), content_type='application/json')

    def test_01_create_kcr_section_a(self):
        res = self.post_project({
            "name": "KCR Section A",
            "track_length_km": 44,
            "discount_rate": 0.08,
            "analysis_period_years": 50
        })
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.json['success'])

    def test_02_create_kcr_section_b(self):
        res = self.post_project({
            "name": "KCR Section B",
            "track_length_km": 100,
            "discount_rate": 0.05,
            "analysis_period_years": 30
        })
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.json['success'])

    def test_03_missing_project_name(self):
        res = self.post_project({
            "name": "",
            "track_length_km": 44,
            "discount_rate": 0.08,
            "analysis_period_years": 50
        })
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['field'], 'name')

    def test_04_negative_track_length(self):
        res = self.post_project({
            "name": "Negative Track",
            "track_length_km": -5,
            "discount_rate": 0.08,
            "analysis_period_years": 50
        })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['field'], 'track_length_km')

    def test_05_invalid_discount_rate(self):
        res = self.post_project({
            "name": "Invalid DR",
            "track_length_km": 50,
            "discount_rate": 1.5, # > 1
            "analysis_period_years": 50
        })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['field'], 'discount_rate')

    def test_06_duplicate_project_name(self):
        # KCR Section A already created in test 1
        res = self.post_project({
            "name": "KCR Section A",
            "track_length_km": 10,
            "discount_rate": 0.08,
            "analysis_period_years": 50
        })
        self.assertEqual(res.status_code, 409)
        self.assertEqual(res.json['field'], 'name')

    def test_07_empty_json(self):
        res = self.client.post('/api/projects', data=json.dumps({}), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['field'], 'payload')

    def test_08_invalid_data_types(self):
        res = self.post_project({
            "name": "Type Test",
            "track_length_km": "invalid_string",
            "discount_rate": 0.08,
            "analysis_period_years": 50
        })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['field'], 'track_length_km')

    def test_09_sql_injection(self):
        res = self.post_project({
            "name": "DROP TABLE projects;--",
            "track_length_km": 50,
            "discount_rate": 0.08,
            "analysis_period_years": 50
        })
        # Should succeed because SQLAlchemy uses parameterized queries
        self.assertEqual(res.status_code, 201)

    def test_10_missing_required_fields(self):
        res = self.post_project({
            "track_length_km": 50,
            "discount_rate": 0.08,
            "analysis_period_years": 50
        }) # No name
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['field'], 'name')

if __name__ == '__main__':
    unittest.main()
