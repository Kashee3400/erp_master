# tests.py - Unit tests
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from ..models.excel_model import ExcelUploadSession
from ..utils.exce_util import ExcelDataProcessor
import pandas as pd
import io


class ExcelDataProcessorTests(TestCase):
    def test_detect_data_types(self):
        """Test data type detection"""
        data = {
            'boolean_col': ['true', 'false', 'yes', 'no'],
            'number_col': [1, 2, 3, 4],
            'date_col': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04'],
            'text_col': ['hello', 'world', 'test', 'data']
        }
        df = pd.DataFrame(data)

        types = ExcelDataProcessor.detect_data_types(df)

        self.assertEqual(types['boolean_col'], 'boolean')
        self.assertEqual(types['number_col'], 'number')
        self.assertEqual(types['date_col'], 'date')
        self.assertEqual(types['text_col'], 'text')


class ExcelUploadAPITests(APITestCase):
    def test_excel_upload_preview(self):
        """Test Excel file upload and preview"""
        # Create a simple Excel file in memory
        data = {'Name': ['John', 'Jane'], 'Age': [30, 25]}
        df = pd.DataFrame(data)

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_sheet(writer, index=False, sheet_name='Sheet1')
        excel_buffer.seek(0)

        uploaded_file = SimpleUploadedFile(
            "test.xlsx",
            excel_buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response = self.client.post('/api/excel/upload/', {
            'file': uploaded_file
        }, format='multipart')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertIn('sheets', response.json())
