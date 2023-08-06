from typing import Union, cast

from jinja2 import Template

KATExchange = dict[str, str]

KATNameAndValues = list[dict[str, Union[str, list[KATExchange]]]]


class KATPrinter:
    _STRING_ANY = """
{%- for document in documents -%}
{%- for x in document -%}
{{ x }} = {{ document[x] }}{% if not loop.last %}
{% endif %}{% endfor %}{% if not loop.last %}
{% endif %}
{% endfor %}"""

    def generate_as_string(self, content: list[dict[str, str]]) -> str:
        """Creates content of the KAT file

        Args:
            content (list): the kat content for the template

        Returns:
            str: string containing the KAT
        """
        template = Template(self._STRING_ANY)
        render = template.render(documents=content)
        return cast(str, render)
