__version__ = '0.1.0'
__author__ = '4molybdenum2'

import json
import os
import requests

from jinja2 import nodes
from jinja2.ext import Extension
from jinja2.nodes import Const
from pathlib import Path


ORGANIZATION = os.getenv("ORGANIZATION", None)
WORKSPACE = os.getenv("WORKSPACE", None)
# Required inputs
# - org_name, workspace_name, state_output_name
class TerraformQueryExtension(Extension):
    tags = {'terraform_query'}

    def parse(self, parser):
        line_number = next(parser.stream).lineno
        
        name = parser.parse_expression()
        parser.stream.skip_if('comma')

        org_name = nodes.Const(ORGANIZATION)
        workspace_name = nodes.Const(WORKSPACE)

        if parser.stream.skip_if('name:organization'):
            parser.stream.skip(1)
            org_name = parser.parse_expression()

        if parser.stream.skip_if('name:workspace'):
            parser.stream.skip(1)
            workspace_name = parser.parse_expression()

        if (not isinstance(org_name, nodes.Const)) or (not org_name.value):
            parser.fail("Organization not specified", lineno=lineno)
        
        if (not isinstance(workspace_name, nodes.Const)) or (not workspace_name.value):
            parser.fail("Workspace not specified", lineno=lineno)

        args = (name, org_name, workspace_name)

        return nodes.Output(
            [self.call_method('_access_state_output', args)], lineno=lineno
        )
    
    def _access_state_output(self, name, org_name, workspace_name):
        return self._get_outputs(name, org_name, workspace_name)
    
    # get org and workspace from env variables but prefer invocation vars
    def _get_outputs(name, org_name, workspace_name):
        TFC_URL = 'https://app.terraform.io/'
        BASE_URL = f'{TFC_URL}/api/v2'

        with open(f'{Path.home()}/.terraform.d/credentials.tfrc.json', 'r') as f:
            config = json.load(f)
            TFC_TOKEN = config['credentials']['app.terraform.io']['token']
        headers = {
            "Authorization": f"Bearer {TFC_TOKEN}",
            "Content-Type": "application/vnd.api+json"
        }

        s = requests.Session()
        s.headers.update(headers)

        workspace_url = f'{BASE_URL}/organizations/{org_name}/workspaces/{workspace_name}'
        resp = s.get(workspace_url)
        search_listed_ws = resp.json()
        ws_id = search_listed_ws['data']['id']

        state_output_url = f'{BASE_URL}/workspaces/{ws_id}/current-state-version-outputs'
        resp = s.get(state_output_url)
        current_state_version_outputs = resp.json()
        current_state_version_outputs = current_state_version_outputs["data"]

        for output in current_state_version_outputs:
            if(output["attributes"]["name"] == name):
                return output["attributes"]["value"]
