from abc import ABC, abstractmethod
from typing import Dict, Any, List
import google.generativeai as genai

class BaseTool(ABC):
    """Base class for all tools"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for OpenRouter function calling"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for OpenRouter"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """OpenRouter function parameters schema"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        pass
    
    def to_openrouter_schema(self) -> Dict[str, Any]:
        """Convert tool to OpenRouter function schema"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

    def to_gemini_schema(self):
        """Convert tool to Gemini FunctionDeclaration schema using official format"""
        # Clean parameters for Gemini compatibility
        clean_params = self._clean_parameters_for_gemini(self.parameters)
        
        # Convert to Gemini Schema format
        gemini_params = self._convert_to_gemini_schema(clean_params)
        
        return genai.types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=gemini_params
        )
    
    def _convert_to_gemini_schema(self, params):
        """Convert OpenAPI schema to Gemini Schema format"""
        if not isinstance(params, dict):
            return params
        
        # Convert type strings to simple strings (Gemini accepts string types)
        type_mapping = {
            "object": "object",
            "string": "string", 
            "integer": "integer",
            "number": "number",
            "boolean": "boolean",
            "array": "array"
        }
        
        schema_dict = {}
        
        if "type" in params:
            schema_dict["type"] = type_mapping.get(params["type"], "string")
        
        if "properties" in params:
            properties = {}
            for prop_name, prop_schema in params["properties"].items():
                properties[prop_name] = self._convert_to_gemini_schema(prop_schema)
            schema_dict["properties"] = properties
        
        if "required" in params:
            schema_dict["required"] = params["required"]
        
        if "description" in params:
            schema_dict["description"] = params["description"]
        
        if "items" in params:
            schema_dict["items"] = self._convert_to_gemini_schema(params["items"])
        
        # Return simple dict instead of Schema object
        return schema_dict
    
    def _clean_parameters_for_gemini(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove fields not supported by Gemini from parameter schema"""
        if not isinstance(params, dict):
            return params
        
        cleaned = {}
        for key, value in params.items():
            if key == "default":
                # Skip 'default' field as it's not supported by Gemini
                continue
            elif isinstance(value, dict):
                # Recursively clean nested dictionaries
                cleaned[key] = self._clean_parameters_for_gemini(value)
            elif isinstance(value, list):
                # Clean items in lists
                cleaned[key] = [
                    self._clean_parameters_for_gemini(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                cleaned[key] = value
        
        return cleaned