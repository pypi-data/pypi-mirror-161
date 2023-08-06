from pathlib import Path
from typing import Dict

from jinja2 import Template


async def render(
    hub,
    ctx,
    name: str,
    template_file_name: str = None,
    template: str = None,
    variables: Dict = None,
):
    """
    A state to render data from jinja template file or an embedded jinja template.
    Templates are a useful way to break off complex logic and have shared functionality.

    Args:
        name(Text): The name of the state.
        template_file_name(Text, Optional): Full path to a jinja template file.
        template(Text, Optional): Embedded Jinja template within {% raw %} {% endraw %}.
            either template or template_file_name should be specified
        variables(Dict, Optional): Variables for interpolation within the template.

    Returns:
        {"result": True|False, "comment": "A message", "old_state": {},
        "new_state": {"rendered": output_content}}

    Request Syntax:
        [output-id]:
          template.render:
           - name: 'string'
           - template_file_name: 'string'
           - variables: Dict

    Example: aws_auth_config_map.tpl has the below content which can be shared in multiple sls files.

    .. code-block::

        {% for user in users_list %}
        - userarn: arn:aws:iam::{{ aws_caller_identity }}:user/{{ user }}
          username: {{ user }}
          groups:
           - system:masters
        {% endfor %}
        {% for svc_user in svc_user %}
        - userarn: arn:aws:iam::{{ aws_caller_identity }}:user/eks/{{ svc_user }}/{{ svc_user }}
          username: {{ svc_user }}
          groups:
           - cluster: {{ svc_user }}
        {% endfor %}

    .. code-block:: sls

        template_render_test:
          template.render:
            - name: template_render_test
            - template_file_name: "/home/files/templates/aws_auth_config_map.tpl"
            - variables:
                users_list: ["user1", "user2"]
                svc_user: ["user1", "user2"]
                aws_caller_identity: "123456789012"

        kubernetes_config_map.aws_auth:
          k8s.core.v1.config_map.present:
            - metadata:
                name: "aws-auth"
                namespace: "kube-system"
            - data:
                mapUsers: ${template:template_render_test:rendered}


        After rendering the template 'aws_auth_config_map.tpl', the output of the state 'template_render_test' will be:

        - userarn: arn:aws:iam::123456789012:user/user1
          username: user1
          groups:
            - system:masters

        - userarn: arn:aws:iam::123456789012:user/user2
          username: user2
          groups:
            - system:masters

        - userarn: arn:aws:iam::123456789012:user/eks/user1/user1
          username: user1
          groups:
            - cluster: user1

        - userarn: arn:aws:iam::123456789012:user/eks/user2/user2
          username: user2
          groups:
            - cluster: user2

        this rendered data will be passed as input to the state 'kubernetes_config_map.aws_auth'

    """
    result = dict(comment=(), old_state={}, new_state={}, name=name, result=True)
    output_content = ""

    if ctx.get("test", False):
        result["comment"] = (f"Would render the template '{name}'.",)
        return result

    if template_file_name is None and template is None:
        result["comment"] = (
            "Either template_file_name or template should be provided",
        )
        result["result"] = False
        return result

    # Jinja template file
    if template_file_name is not None:
        template_file = Path(template_file_name)
        if template_file.is_file() is False:
            msg = f"Template file not found: {template_file_name}"
            hub.log.debug(msg)
            result["result"] = False
            result["comment"] = (msg,)
            return result
        else:
            with open(template_file) as curr_template_file:
                tm = Template(curr_template_file.read())
                output_content = tm.render(**variables) if variables else tm.render()
    # Embedded Jinja template
    elif template is not None:
        tm = Template(template)
        output_content = tm.render(**variables) if variables else tm.render()

    result["comment"] = (f"Template rendering is success",)
    # The final rendered template
    result["new_state"] = {"rendered": output_content}
    return result
