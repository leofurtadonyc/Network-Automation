from jinja2 import Environment, FileSystemLoader

def render_template(template_name, context):
    """Render customer configuration from Jinja2 templates."""
    env = Environment(loader=FileSystemLoader('templates/'))
    template = env.get_template(template_name)
    return template.render(context)
