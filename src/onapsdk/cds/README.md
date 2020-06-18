# CDS module #

## Load blueprint ##

```
>>> from onapsdk.cds import Blueprint
>>> blueprint = Blueprint.load_from_file("<< path to CBA file >>")  # load a blueprint from ZIP file
```

## Enrich, publish, deploy blueprint

```
>>> enriched_blueprint = blueprint.enrich()  # returns enriched blueprint object
>>> enriched_blueprint.publish()
>>> enriched_blueprint.deploy()
```

## Execute blueprint workflow

```
>>> blueprint.workflows
[Workflow(name='resource-assignment', blueprint_name='vDNS-CDS-test1)', Workflow(name='config-assign', blueprint_name='vDNS-CDS-test1)', Workflow(name='config-deploy', blueprint_name='vDNS-CDS-test1)']
>>> workflow = blueprint.workflows[0]  # get the first workflow named 'resource-assignment`
>>> workflow.inputs  # display what workflow needs as an input
[Workflow.WorkflowInput(name='template-prefix', required=True, type='list', description=None), Workflow.WorkflowInput(name='resource-assignment-properties', required=True, type='dt-resource-assignment-properties', description='Dynamic PropertyDefinition for workflow(resource-assignment).')]
>>> response = workflow.execute({"template-prefix": ["vpkg"], "resource-assignment-properties": {}})  # execute workflow with required inputs
```

## Generate data dictionary for blueprint

Generated data dictionaries have to be manualy filled for "source-rest" and "source-db" input types.

```
>>> blueprint.get_data_dictionaries().save_to_file("/tmp/dd.json")  # generate data dictionaries for blueprint and save it to "/tmp/dd.json" file
```