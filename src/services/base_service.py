#!/usr/bin/env python3
"""
Base Service Class for Kolekt
Provides common functionality for all services
"""

import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """Base class for all Kolekt services"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(f"{__name__}.{service_name}")
        self.initialized = False
        self.config: Dict[str, Any] = {}
        
        self.logger.info(f"Initializing {service_name} service")
    
    async def initialize(self) -> bool:
        """Initialize the service"""
        try:
            await self._initialize_service()
            self.initialized = True
            self.logger.info(f"{self.service_name} service initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.service_name} service: {e}")
            return False
    
    @abstractmethod
    async def _initialize_service(self):
        """Service-specific initialization logic"""
        pass
    
    async def shutdown(self):
        """Shutdown the service"""
        try:
            await self._shutdown_service()
            self.initialized = False
            self.logger.info(f"{self.service_name} service shut down successfully")
        except Exception as e:
            self.logger.error(f"Error shutting down {self.service_name} service: {e}")
    
    async def _shutdown_service(self):
        """Service-specific shutdown logic"""
        pass
    
    def is_healthy(self) -> bool:
        """Check if the service is healthy"""
        return self.initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "service_name": self.service_name,
            "initialized": self.initialized,
            "healthy": self.is_healthy(),
            "config": self.config
        }
    
    def update_config(self, config: Dict[str, Any]):
        """Update service configuration"""
        self.config.update(config)
        self.logger.info(f"Updated {self.service_name} configuration")


class ServiceManager:
    """Manages all services in the application"""
    
    def __init__(self):
        self.services: Dict[str, BaseService] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_service(self, service: BaseService):
        """Register a service"""
        self.services[service.service_name] = service
        self.logger.info(f"Registered service: {service.service_name}")
    
    async def initialize_all(self):
        """Initialize all registered services"""
        self.logger.info("Initializing all services...")
        
        for service_name, service in self.services.items():
            success = await service.initialize()
            if not success:
                self.logger.warning(f"Service {service_name} failed to initialize")
        
        self.logger.info("Service initialization complete")
    
    async def shutdown_all(self):
        """Shutdown all registered services"""
        self.logger.info("Shutting down all services...")
        
        for service_name, service in self.services.items():
            await service.shutdown()
        
        self.logger.info("Service shutdown complete")
    
    def get_service(self, service_name: str) -> Optional[BaseService]:
        """Get a service by name"""
        return self.services.get(service_name)
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all services"""
        return {
            service_name: service.get_status()
            for service_name, service in self.services.items()
        }
    
    def get_healthy_services(self) -> Dict[str, BaseService]:
        """Get all healthy services"""
        return {
            service_name: service
            for service_name, service in self.services.items()
            if service.is_healthy()
        }


# Global service manager instance
service_manager = ServiceManager()
