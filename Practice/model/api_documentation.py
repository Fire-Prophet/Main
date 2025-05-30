"""
Fire Simulation API Documentation and SDK Generator
Provides comprehensive API documentation and client SDK generation.
"""

import json
import inspect
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass, asdict
from pathlib import Path
import yaml
from datetime import datetime


@dataclass
class APIEndpoint:
    """API endpoint documentation structure."""
    path: str
    method: str
    description: str
    parameters: List[Dict[str, Any]]
    response_schema: Dict[str, Any]
    examples: List[Dict[str, Any]]
    tags: List[str]


@dataclass
class APIDocumentation:
    """Complete API documentation structure."""
    title: str
    version: str
    description: str
    base_url: str
    endpoints: List[APIEndpoint]
    schemas: Dict[str, Any]
    security: Dict[str, Any]


class DocumentationGenerator:
    """Generates comprehensive API documentation."""
    
    def __init__(self):
        self.endpoints = []
        self.schemas = {}
        
    def document_class(self, cls: Type, tag: str = "simulation") -> None:
        """Document all public methods of a class as API endpoints."""
        for method_name, method in inspect.getmembers(cls, predicate=inspect.ismethod):
            if not method_name.startswith('_'):
                self._document_method(method, cls.__name__, tag)
    
    def _document_method(self, method, class_name: str, tag: str) -> None:
        """Document a single method as an API endpoint."""
        signature = inspect.signature(method)
        doc = inspect.getdoc(method) or f"{class_name}.{method.__name__}"
        
        parameters = []
        for param_name, param in signature.parameters.items():
            if param_name != 'self':
                param_doc = {
                    "name": param_name,
                    "type": str(param.annotation) if param.annotation != param.empty else "Any",
                    "required": param.default == param.empty,
                    "default": str(param.default) if param.default != param.empty else None
                }
                parameters.append(param_doc)
        
        endpoint = APIEndpoint(
            path=f"/{class_name.lower()}/{method.__name__}",
            method="POST",
            description=doc,
            parameters=parameters,
            response_schema={"type": "object", "properties": {"result": {"type": "any"}}},
            examples=[{
                "request": {param["name"]: f"example_{param['name']}" for param in parameters},
                "response": {"result": "success", "data": "example_output"}
            }],
            tags=[tag]
        )
        self.endpoints.append(endpoint)
    
    def add_schema(self, name: str, schema: Dict[str, Any]) -> None:
        """Add a data schema to documentation."""
        self.schemas[name] = schema
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Fire Simulation API",
                "version": "1.0.0",
                "description": "Comprehensive API for fire spread simulation and analysis"
            },
            "servers": [
                {"url": "http://localhost:8000", "description": "Local development server"},
                {"url": "https://api.firesim.example.com", "description": "Production server"}
            ],
            "paths": {},
            "components": {
                "schemas": self.schemas,
                "securitySchemes": {
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key"
                    }
                }
            }
        }
        
        for endpoint in self.endpoints:
            path = endpoint.path
            if path not in spec["paths"]:
                spec["paths"][path] = {}
            
            spec["paths"][path][endpoint.method.lower()] = {
                "summary": endpoint.description,
                "tags": endpoint.tags,
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    param["name"]: {"type": param["type"]}
                                    for param in endpoint.parameters
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": endpoint.response_schema
                            }
                        }
                    }
                },
                "security": [{"ApiKeyAuth": []}]
            }
        
        return spec
    
    def save_documentation(self, output_dir: Path) -> None:
        """Save documentation in multiple formats."""
        output_dir.mkdir(exist_ok=True)
        
        # OpenAPI spec
        openapi_spec = self.generate_openapi_spec()
        with open(output_dir / "openapi.json", 'w') as f:
            json.dump(openapi_spec, f, indent=2)
        
        with open(output_dir / "openapi.yaml", 'w') as f:
            yaml.dump(openapi_spec, f, default_flow_style=False)
        
        # Generate HTML documentation
        self._generate_html_docs(output_dir)
        
        # Generate SDK examples
        self._generate_sdk_examples(output_dir)
    
    def _generate_html_docs(self, output_dir: Path) -> None:
        """Generate HTML documentation."""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Fire Simulation API Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .endpoint { border: 1px solid #ddd; margin: 20px 0; padding: 20px; }
        .method { background: #007bff; color: white; padding: 5px 10px; border-radius: 3px; }
        .path { font-family: monospace; background: #f8f9fa; padding: 5px; }
        .param { background: #e9ecef; padding: 10px; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>Fire Simulation API Documentation</h1>
    <p>Generated on: {date}</p>
    
    <h2>Endpoints</h2>
""".format(date=datetime.now().isoformat())
        
        for endpoint in self.endpoints:
            html_content += f"""
    <div class="endpoint">
        <h3><span class="method">{endpoint.method}</span> <span class="path">{endpoint.path}</span></h3>
        <p>{endpoint.description}</p>
        
        <h4>Parameters:</h4>
        {chr(10).join(f'<div class="param"><strong>{p["name"]}</strong> ({p["type"]}) - Required: {p["required"]}</div>' for p in endpoint.parameters)}
        
        <h4>Example Request:</h4>
        <pre>{json.dumps(endpoint.examples[0]["request"], indent=2) if endpoint.examples else "{}"}</pre>
        
        <h4>Example Response:</h4>
        <pre>{json.dumps(endpoint.examples[0]["response"], indent=2) if endpoint.examples else "{}"}</pre>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        with open(output_dir / "documentation.html", 'w') as f:
            f.write(html_content)
    
    def _generate_sdk_examples(self, output_dir: Path) -> None:
        """Generate SDK examples in multiple languages."""
        
        # Python SDK example
        python_sdk = '''
"""Fire Simulation Python SDK"""
import requests
import json
from typing import Dict, Any, Optional

class FireSimulationClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

'''
        
        for endpoint in self.endpoints:
            method_name = endpoint.path.split('/')[-1]
            params = ", ".join([f"{p['name']}: {p['type']}" for p in endpoint.parameters])
            data_dict = "{" + ", ".join([f'"{p["name"]}": {p["name"]}' for p in endpoint.parameters]) + "}"
            
            python_sdk += f'''
    def {method_name}(self, {params}) -> Dict[str, Any]:
        """{endpoint.description}"""
        data = {data_dict}
        return self._make_request("{endpoint.path}", data)
'''
        
        with open(output_dir / "python_sdk.py", 'w') as f:
            f.write(python_sdk)
        
        # JavaScript SDK example
        js_sdk = '''
/**
 * Fire Simulation JavaScript SDK
 */
class FireSimulationClient {
    constructor(baseUrl = "http://localhost:8000", apiKey = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.apiKey = apiKey;
    }
    
    async _makeRequest(endpoint, data) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }
        
        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.statusText}`);
        }
        
        return response.json();
    }

'''
        
        for endpoint in self.endpoints:
            method_name = endpoint.path.split('/')[-1]
            params = ", ".join([p['name'] for p in endpoint.parameters])
            data_obj = "{" + ", ".join([p['name'] for p in endpoint.parameters]) + "}"
            
            js_sdk += f'''
    /**
     * {endpoint.description}
     */
    async {method_name}({params}) {{
        const data = {data_obj};
        return this._makeRequest("{endpoint.path}", data);
    }}
'''
        
        js_sdk += "\n}\n\nmodule.exports = FireSimulationClient;"
        
        with open(output_dir / "javascript_sdk.js", 'w') as f:
            f.write(js_sdk)


class SimulationAPIDocumenter:
    """Main class for documenting the fire simulation API."""
    
    def __init__(self):
        self.doc_generator = DocumentationGenerator()
        self._setup_schemas()
    
    def _setup_schemas(self) -> None:
        """Setup common data schemas."""
        schemas = {
            "GridPoint": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                    "elevation": {"type": "number"},
                    "fuel_type": {"type": "integer"},
                    "moisture": {"type": "number"}
                }
            },
            "WeatherConditions": {
                "type": "object",
                "properties": {
                    "wind_speed": {"type": "number"},
                    "wind_direction": {"type": "number"},
                    "temperature": {"type": "number"},
                    "humidity": {"type": "number"}
                }
            },
            "SimulationResult": {
                "type": "object",
                "properties": {
                    "fire_perimeter": {"type": "array"},
                    "burned_area": {"type": "number"},
                    "simulation_time": {"type": "number"},
                    "metrics": {"type": "object"}
                }
            }
        }
        
        for name, schema in schemas.items():
            self.doc_generator.add_schema(name, schema)
    
    def document_fire_simulation(self) -> None:
        """Document fire simulation classes and methods."""
        # This would normally document actual classes
        # For now, we'll create example endpoint documentation
        
        endpoints = [
            {
                "path": "/simulation/initialize",
                "method": "POST",
                "description": "Initialize a new fire simulation",
                "parameters": [
                    {"name": "grid_size", "type": "tuple", "required": True},
                    {"name": "fuel_map", "type": "array", "required": True},
                    {"name": "weather", "type": "WeatherConditions", "required": True}
                ]
            },
            {
                "path": "/simulation/run",
                "method": "POST", 
                "description": "Run fire simulation for specified time steps",
                "parameters": [
                    {"name": "time_steps", "type": "integer", "required": True},
                    {"name": "ignition_points", "type": "array", "required": True}
                ]
            },
            {
                "path": "/simulation/analyze",
                "method": "POST",
                "description": "Analyze simulation results and generate reports",
                "parameters": [
                    {"name": "simulation_id", "type": "string", "required": True},
                    {"name": "analysis_type", "type": "string", "required": False}
                ]
            }
        ]
        
        for ep_data in endpoints:
            endpoint = APIEndpoint(
                path=ep_data["path"],
                method=ep_data["method"],
                description=ep_data["description"],
                parameters=ep_data["parameters"],
                response_schema={"$ref": "#/components/schemas/SimulationResult"},
                examples=[{
                    "request": {p["name"]: f"example_{p['name']}" for p in ep_data["parameters"]},
                    "response": {"result": "success", "simulation_id": "sim_123"}
                }],
                tags=["simulation"]
            )
            self.doc_generator.endpoints.append(endpoint)
    
    def generate_complete_documentation(self, output_dir: str = "docs/api") -> None:
        """Generate complete API documentation."""
        self.document_fire_simulation()
        
        output_path = Path(output_dir)
        self.doc_generator.save_documentation(output_path)
        
        print(f"API documentation generated in {output_path}")
        print(f"- OpenAPI spec: {output_path}/openapi.json")
        print(f"- HTML docs: {output_path}/documentation.html")
        print(f"- Python SDK: {output_path}/python_sdk.py")
        print(f"- JavaScript SDK: {output_path}/javascript_sdk.js")


if __name__ == "__main__":
    documenter = SimulationAPIDocumenter()
    documenter.generate_complete_documentation()
