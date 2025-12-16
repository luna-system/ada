"""
Specialist Registry - Auto-discovery and management of specialist plugins.

Provides plugin-style extensibility: drop a *_specialist.py file in this directory
and it will be automatically discovered and registered.
"""
import logging
import importlib
import inspect
from pathlib import Path
from typing import Optional, List, Dict, Any

from .protocol import Specialist, SpecialistResult, SpecialistPriority

logger = logging.getLogger(__name__)


class SpecialistRegistry:
    """
    Central registry for all specialist plugins.
    Handles discovery, activation, and execution.
    """
    
    def __init__(self):
        self._specialists: List[Specialist] = []
        self._by_name: Dict[str, Specialist] = {}
        self._initialized = False
    
    def discover_specialists(self):
        """
        Auto-discover specialist plugins in this directory.
        Looks for *_specialist.py files and loads classes implementing Specialist protocol.
        """
        if self._initialized:
            logger.warning("Registry already initialized, skipping discovery")
            return
        
        logger.info("Discovering specialist plugins...")
        specialists_dir = Path(__file__).parent
        
        # Find all *_specialist.py files
        for module_path in specialists_dir.glob("*_specialist.py"):
            module_name = module_path.stem
            try:
                # Import the module
                module = importlib.import_module(f"brain.specialists.{module_name}")
                
                # Look for classes implementing Specialist protocol
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Check if it's a Specialist (structural typing check)
                    if self._is_specialist_class(obj):
                        try:
                            # Instantiate the specialist
                            instance = obj()
                            self.register(instance)
                            logger.info(f"Loaded specialist: {instance.capability.name} from {module_name}")
                        except Exception as e:
                            logger.error(f"Failed to instantiate {name} from {module_name}: {e}")
            
            except Exception as e:
                logger.error(f"Failed to load specialist module {module_name}: {e}")
        
        self._initialized = True
        logger.info(f"Specialist discovery complete. Registered: {list(self._by_name.keys())}")
    
    def _is_specialist_class(self, obj) -> bool:
        """Check if a class implements the Specialist protocol"""
        # Must be a class, not an instance
        if not inspect.isclass(obj):
            return False
        
        # Exclude Protocol classes themselves and BaseSpecialist
        obj_name = obj.__name__
        if obj_name in ('Specialist', 'BaseSpecialist'):
            return False
        
        # Check for required methods/properties
        required = ['capability', 'process', 'should_activate']
        return all(hasattr(obj, attr) for attr in required)
    
    def register(self, specialist: Specialist):
        """Manually register a specialist instance"""
        name = specialist.capability.name
        
        if name in self._by_name:
            logger.warning(f"Specialist '{name}' already registered, replacing")
        
        self._specialists.append(specialist)
        self._by_name[name] = specialist
    
    def get(self, name: str) -> Optional[Specialist]:
        """Get specialist by name"""
        return self._by_name.get(name)
    
    def list_all(self) -> List[Specialist]:
        """List all registered specialists"""
        return self._specialists.copy()
    
    def list_enabled(self) -> List[Specialist]:
        """List only enabled specialists"""
        return [s for s in self._specialists if s.capability.enabled]
    
    async def execute_for_context(self, request_context: dict) -> List[SpecialistResult]:
        """
        Execute all specialists that should activate for the given request context.
        
        Args:
            request_context: Request metadata dict (prompt, conversation_id, etc.)
            
        Returns:
            List of SpecialistResult from activated specialists, sorted by priority
        """
        if not self._initialized:
            self.discover_specialists()
        
        results = []
        
        for specialist in self.list_enabled():
            try:
                # Check if specialist should activate
                if specialist.should_activate(request_context):
                    logger.debug(f"Activating specialist: {specialist.capability.name}")
                    
                    # Execute specialist
                    result = await specialist.process(**request_context)
                    results.append(result)
                    
                    if not result.success:
                        logger.warning(f"Specialist {specialist.capability.name} failed: {result.error}")
            
            except Exception as e:
                logger.error(f"Exception in specialist {specialist.capability.name}: {e}", exc_info=True)
                # Continue with other specialists
        
        # Sort by priority (lower priority number = earlier in prompt)
        results.sort(key=lambda r: self._get_priority(r.specialist_name))
        
        return results
    
    def _get_priority(self, specialist_name: str) -> int:
        """Get priority value for sorting"""
        specialist = self._by_name.get(specialist_name)
        if specialist:
            return specialist.capability.context_priority.value
        return SpecialistPriority.MEDIUM.value


# Global registry instance
_registry: Optional[SpecialistRegistry] = None


def get_registry() -> SpecialistRegistry:
    """Get or create the global specialist registry"""
    global _registry
    if _registry is None:
        _registry = SpecialistRegistry()
        _registry.discover_specialists()
    return _registry


# Convenience functions
def list_specialists() -> List[Specialist]:
    """List all registered specialists"""
    return get_registry().list_all()


def get_specialist(name: str) -> Optional[Specialist]:
    """Get specialist by name"""
    return get_registry().get(name)


async def execute_specialists(request_context: dict) -> List[SpecialistResult]:
    """Execute all applicable specialists for a request"""
    return await get_registry().execute_for_context(request_context)
