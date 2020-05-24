# -*- coding: utf-8 -*-

"""# Functions for getting and setting style DEPEDENDENCIES, organized into sections:

I. General functions for getting and setting dependencies
II. Specific functions for setting particular dependencies
"""

# External library imports
import sys
import time

# Internal module imports
from . import commands
from . import styles

# Internal module convenience imports
from .exceptions import CyError
from .py4cytoscape_utils import *
from .py4cytoscape_logger import cy_log
from .py4cytoscape_tuning import MODEL_PROPAGATION_SECS

# ==============================================================================
# I. General Functions
# ------------------------------------------------------------------------------

@cy_log
def get_style_dependencies(style_name='default', base_url=DEFAULT_BASE_URL):
    """Get the values of dependencies in a style.

    Args:
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: contains all dependencies and their current boolean value

    Raises:
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> get_style_dependencies(style_name='galFiltered Style')
        {'arrowColorMatchesEdge': False, 'nodeCustomGraphicsSizeSync': True, 'nodeSizeLocked': True}
        >>> get_style_dependencies()
        {'arrowColorMatchesEdge': False, 'nodeCustomGraphicsSizeSync': True, 'nodeSizeLocked': False}
    """
    # launch error if visual style name is missing
    if style_name not in styles.get_visual_style_names(base_url=base_url):
        error = 'Error in py4cytoscape:get_style_dependencies. No visual style named "' + style_name + '"'
        # TODO: R version of this error has the wrong text
        sys.stderr.write(error)
        raise CyError(error)
    #        return None
    # TODO: Is this what we want to return here?

    res = commands.cyrest_get('styles/' + style_name + '/dependencies', base_url=base_url)

    # make it a dict
    dep_list = {dep['visualPropertyDependency']: dep['enabled'] for dep in res}
    return dep_list

@cy_log
def set_style_dependencies(style_name='default', dependencies={}, base_url=DEFAULT_BASE_URL):
    """Set the values of dependencies in a style, overriding any prior setting.

    Args:
        style_name (str): Name of style; default is "default" style
        dependencies (dict): A ``list`` of style dependencies, see Available Dependencies below. Note: each dependency
            is set by a boolean, True or False
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: contains the ``views`` property with a value of the current view's SUID (e.g., {'views': [275240]})

    Raises:
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> set_style_dependencies(dependencies={'arrowColorMatchesEdge': True}, style_name='galFiltered Style')
        {'views': [275240]}
        >>> get_style_dependencies(dependencies={'arrowColorMatchesEdge': True, 'nodeCustomGraphicsSizeSync': False})
        {'views': [275240]}

    Available Dependencies:
        arrowColorMatchesEdge, nodeCustomGraphicsSizeSync, nodeSizeLocked
    """
    # launch error if visual style name is missing
    if style_name not in styles.get_visual_style_names(base_url=base_url):
        error = 'Error in py4cytoscape:set_style_dependencies. No visual style named "' + style_name + '"'
        # TODO: R version of this error has the wrong text
        sys.stderr.write(error)
        raise CyError(error)
        # return None
        # TODO: Is this what we want to return here?

    dep_list = [{'visualPropertyDependency': dep, 'enabled': val}    for dep, val in dependencies.items()]

    res = commands.cyrest_put('styles/' + style_name + '/dependencies', body=dep_list, base_url=base_url, require_json=False)
    res = commands.commands_post('vizmap apply styles="' + style_name + '"')
    # TODO: Do we really want to lose the first res value?
    return res


# ==============================================================================
# II. Specific Functions
# Pattern: (1) Call setStyleDependencies()
# ------------------------------------------------------------------------------

@cy_log
def match_arrow_color_to_edge(new_state, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set a boolean value to have arrow shapes share the same color as the edge.

    Args:
        new_state (bool): Whether to match arrow color to edge.
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: contains the ``views`` property with a value of the current view's SUID (e.g., {'views': [275240]})

    Raises:
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> match_arrow_color_to_edge(True, style_name='galFiltered Style')
        {'views': [275240]}
        >>> match_arrow_color_to_edge(False)
        {'views': [275240]}
    """
    toggle = 'true' if new_state else 'false'

    res = set_style_dependencies(style_name=style_name, dependencies={'arrowColorMatchesEdge': toggle}, base_url=base_url)

    return res

@cy_log
def lock_node_dimensions(new_state, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set a boolean value to have node width and height fixed to a single size value.

    Args:
        new_state (bool): Whether to lock node width and height
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: contains the ``views`` property with a value of the current view's SUID (e.g., {'views': [275240]})

    Raises:
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> lock_node_dimensions(True, style_name='galFiltered Style')
        {'views': [275240]}
        >>> lock_node_dimensions(False)
        {'views': [275240]}
    """
    toggle = 'true' if new_state else 'false'

    res = set_style_dependencies(style_name=style_name, dependencies={'nodeSizeLocked': toggle}, base_url=base_url)

    return res

@cy_log
def sync_node_custom_graphics_size(new_state, style_name='default', base_url=DEFAULT_BASE_URL):
    """Set a boolean value to have the size of custom graphics match that of the node.

    Args:
        new_state (bool): Whether to sync node custom graphics size
        style_name (str): Name of style; default is "default" style
        base_url (str): Ignore unless you need to specify a custom domain,
            port or version to connect to the CyREST API. Default is http://localhost:1234
            and the latest version of the CyREST API supported by this version of py4cytoscape.

    Returns:
        dict: contains the ``views`` property with a value of the current view's SUID (e.g., {'views': [275240]})

    Raises:
        CyError: if style name doesn't exist
        requests.exceptions.RequestException: if can't connect to Cytoscape or Cytoscape returns an error

    Examples:
        >>> sync_node_custom_graphics_size(True, style_name='galFiltered Style')
        {'views': [275240]}
        >>> sync_node_custom_graphics_size(False)
        {'views': [275240]}
    """
    toggle = 'true' if new_state else 'false'

    res = set_style_dependencies(style_name=style_name, dependencies={'nodeCustomGraphicsSizeSync': toggle}, base_url=base_url)

    return res