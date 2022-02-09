
_templates = None


def get_templates():
    global _templates
    if _templates is None:
        import os
        from jinja2 import Environment, FileSystemLoader
        from ._filters import custom_filters
        env = Environment(loader=FileSystemLoader(searchpath=os.path.dirname(os.path.abspath(__file__))))
        env.filters.update(custom_filters)
        _templates = {}
        # _templates['tree'] = env.get_template("tree.md.j2")
    return _templates
