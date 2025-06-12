from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ErrorLevel(str, Enum):
    FATAL = "fatal"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class ExceptionInfo(BaseModel):
    """Exception information similar to Sentry's format"""
    type: str = Field(..., description="Exception class name")
    value: str = Field(..., description="Exception message")
    module: Optional[str] = Field(None, description="Module where exception occurred")


class UserContext(BaseModel):
    """User context information"""
    id: Optional[str] = Field(None, description="User ID")
    username: Optional[str] = Field(None, description="Username")
    email: Optional[str] = Field(None, description="User email")
    ip_address: Optional[str] = Field(None, description="User IP address")


class RequestContext(BaseModel):
    """HTTP request context"""
    method: Optional[str] = Field(None, description="HTTP method")
    url: Optional[str] = Field(None, description="Request URL")
    headers: Optional[Dict[str, str]] = Field(None, description="Request headers")
    query_string: Optional[str] = Field(None, description="Query string")
    data: Optional[Any] = Field(None, description="Request data")


class ErrorPayload(BaseModel):
    # Project/Service identification (MVP: using service as project_id)
    service: str = Field(..., description="Service/project identifier")
    environment: str = Field(default="production", description="Environment name")
    
    # Error details
    message: str = Field(..., description="Error message")
    level: ErrorLevel = Field(default=ErrorLevel.ERROR, description="Error severity level")
    
    # Exception information (MVP: structured exception data)
    exception: Optional[ExceptionInfo] = Field(None, description="Exception information")
    
    # Context (MVP: basic context support)
    tags: Dict[str, str] = Field(default_factory=dict, description="Custom tags")
    extra: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")
    
    # User context (MVP: basic user tracking)
    user: Optional[UserContext] = Field(None, description="User context")
    
    # Request context (MVP: basic request tracking)
    request: Optional[RequestContext] = Field(None, description="HTTP request context")
    
    # Metadata (MVP: basic metadata)
    timestamp: Optional[datetime] = Field(None, description="Error timestamp")
    release: Optional[str] = Field(None, description="Application release version")
    
    # Legacy fields for backward compatibility
    error_type: Optional[str] = Field(None, description="Error type (legacy)")
    stack_trace: Optional[str] = Field(None, description="Stack trace as string (legacy)")
    error_metadata: Optional[Dict[str, Any]] = Field(None, description="Error metadata (legacy)")