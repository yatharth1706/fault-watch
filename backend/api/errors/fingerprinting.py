import hashlib
import json
from typing import List, Optional
from .schema import ErrorPayload, ExceptionInfo


class ErrorFingerprinter:
    """
    Generates unique fingerprints for errors to group similar errors together.
    Similar to Sentry's fingerprinting algorithm.
    """
    
    def generate_fingerprint(self, error: ErrorPayload) -> str:
        """
        Generate a unique fingerprint for an error based on its characteristics.
        """
        # Start with exception type and value if available
        if error.exception:
            fingerprint_parts = [
                error.exception.type,
                error.exception.value
            ]
        else:
            # Fallback to message for non-exception errors
            fingerprint_parts = [error.message]
        
        # Add service and environment for isolation
        fingerprint_parts.extend([
            error.service,
            error.environment
        ])
        
        # Create hash from fingerprint parts
        fingerprint_string = "|".join(filter(None, fingerprint_parts))
        return hashlib.md5(fingerprint_string.encode()).hexdigest()
    
    def generate_title(self, error: ErrorPayload) -> str:
        """
        Generate a human-readable title for the error group.
        """
        if error.exception:
            return f"{error.exception.type}: {error.exception.value}"
        return error.message[:100] + "..." if len(error.message) > 100 else error.message
    
    def generate_culprit(self, error: ErrorPayload) -> str:
        """
        Generate a culprit string indicating where the error occurred.
        For MVP, we'll use a simple approach based on service and exception type.
        """
        if error.exception:
            return f"{error.service} in {error.exception.type}"
        return f"{error.service} in unknown"
    
    def should_group_errors(self, error1: ErrorPayload, error2: ErrorPayload) -> bool:
        """
        Determine if two errors should be grouped together.
        """
        return (
            self.generate_fingerprint(error1) == self.generate_fingerprint(error2)
        )
    
    def get_grouping_key(self, error: ErrorPayload) -> str:
        """
        Get a grouping key for database queries.
        This is a simpler version of the fingerprint for database indexing.
        """
        if error.exception:
            return f"{error.service}:{error.environment}:{error.exception.type}"
        return f"{error.service}:{error.environment}:message" 