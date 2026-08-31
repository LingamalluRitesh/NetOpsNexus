"""
Jinja2 Configuration Template Engine with strict parameter checking and syntax validation.
"""

from typing import Dict, Any, List, Tuple
from jinja2 import Environment, StrictUndefined, meta
from backend.app.configurations.schemas import TemplateRenderResponse


class ConfigTemplateEngine:
    def __init__(self):
        self.env = Environment(undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)

    def extract_variables(self, template_text: str) -> List[str]:
        """Extract all expected variable names from Jinja2 template string."""
        ast = self.env.parse(template_text)
        return list(meta.find_undeclared_variables(ast))

    def render_template(self, template_text: str, variables: Dict[str, Any]) -> TemplateRenderResponse:
        """Render template with supplied parameters and validate output syntax."""
        errors = []
        try:
            template = self.env.from_string(template_text)
            rendered = template.render(**variables)
            
            # Basic network CLI syntax validations
            if "interface" in rendered and not any(k in rendered for k in ["no shutdown", "shutdown", "switchport", "ip address"]):
                errors.append("Warning: Interface configuration block has no action commands specified")

            return TemplateRenderResponse(
                rendered_config=rendered,
                variables_used=variables,
                syntax_valid=len(errors) == 0,
                errors=errors,
            )
        except Exception as e:
            return TemplateRenderResponse(
                rendered_config="",
                variables_used=variables,
                syntax_valid=False,
                errors=[f"Template rendering error: {str(e)}"],
            )
