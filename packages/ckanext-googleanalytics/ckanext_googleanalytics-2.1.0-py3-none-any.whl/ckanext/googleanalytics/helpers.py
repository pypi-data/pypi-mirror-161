import ckan.plugins.toolkit as tk
from ckanext.googleanalytics import utils


def get_helpers():
    return {
        "googleanalytics_header": googleanalytics_header,
        "googleanalytics_resource_prefix": googleanalytics_resource_prefix,
    }


def googleanalytics_resource_prefix():

    return utils.config_prefix()


def googleanalytics_header():
    """Render the googleanalytics_header snippet for CKAN 2.0 templates.

    This is a template helper function that renders the
    googleanalytics_header jinja snippet. To be called from the jinja
    templates in this extension, see ITemplateHelpers.

    """

    fields = utils.config_fields()

    if utils.config_enable_user_id() and tk.c.user:
        fields["userId"] = str(tk.c.userobj.id)

    data = {
        "googleanalytics_id": utils.config_id(),
        "googleanalytics_domain": utils.config_domain(),
        "googleanalytics_fields": str(fields),
        "googleanalytics_linked_domains": utils.config_linked_domains(),
    }
    return tk.render_snippet(
        "googleanalytics/snippets/googleanalytics_header.html", data
    )
