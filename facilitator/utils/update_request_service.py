# utils.py
from django.db import transaction
from typing import Dict, Any, Optional, List
import json
from ..models.member_update_model import User,UpdateRequest,UpdateRequestData,UpdateRequestDocument
from ..choices import *


class UpdateRequestService:
    """Service class for handling update request operations"""
    
    @staticmethod
    def create_update_request(
        facilitator: User,
        member_code: str,
        member_name: str,
        mobile_number: str,
        role_type: str,
        request_type: str,
        update_data: Dict[str, Any],
        documents: Optional[List[Dict]] = None
    ) -> UpdateRequest:
        """
        Create a new update request with data and documents
        """
        with transaction.atomic():
            # Create main request
            request = UpdateRequest.objects.create(
                member_code=member_code,
                member_name=member_name,
                mobile_number=mobile_number,
                role_type=role_type,
                request_type=request_type,
                created_by=facilitator,
                updated_by=facilitator
            )
            
            # Add update data
            for field_name, value in update_data.items():
                if value is not None:
                    data_type = 'json' if isinstance(value, (dict, list)) else 'text'
                    UpdateRequestData.objects.create(
                        request=request,
                        field_name=field_name,
                        new_value=json.dumps(value) if data_type == 'json' else str(value),
                        data_type=data_type,
                        created_by=facilitator
                    )
            
            # Add documents
            if documents:
                for doc_data in documents:
                    UpdateRequestDocument.objects.create(
                        request=request,
                        document_type=doc_data['document_type'],
                        file=doc_data['file'],
                        original_filename=doc_data['original_filename'],
                        file_size=doc_data['file_size'],
                        content_type=doc_data['content_type'],
                        description=doc_data.get('description', ''),
                        created_by=facilitator
                    )
            
            return request
    
    @staticmethod
    def get_request_history(request: UpdateRequest) -> List[Dict]:
        """Get formatted history for a request"""
        history = request.history.all().order_by('-created_at')
        return [
            {
                'id': h.id,
                'change_type': h.get_change_type_display(),
                'field_name': h.field_name,
                'old_value': h.old_value,
                'new_value': h.new_value,
                'changed_by': h.changed_by.username,
                'changed_at': h.created_at,
                'reason': h.change_reason,
                'metadata': h.metadata
            }
            for h in history
        ]
    
    @staticmethod
    def get_request_data(request: UpdateRequest) -> Dict[str, Any]:
        """Get all data for a request"""
        data = {}
        for item in request.request_data.all():
            data[item.field_name] = item.parsed_new_value
        return data
    
    @staticmethod
    def update_request_status(
        request: UpdateRequest,
        status: str,
        user: User,
        reason: Optional[str] = None,
        comments: Optional[str] = None
    ) -> UpdateRequest:
        """Update request status with proper logging"""
        request._current_user = user
        
        if status == RequestStatus.APPROVED:
            request.approve(user, comments)
        elif status == RequestStatus.REJECTED:
            request.reject(user, reason or "No reason provided", comments)
        else:
            request.status = status
            request.updated_by = user
            request.save()
        
        return request

