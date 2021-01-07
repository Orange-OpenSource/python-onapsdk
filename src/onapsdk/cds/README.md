# CDS module #

## Load blueprint ##

```
>>> from onapsdk.cds import Blueprint
>>> blueprint = Blueprint.load_from_file("<< path to CBA file >>")  # load a blueprint from ZIP file
```

## Enrich, publish blueprint

```
>>> enriched_blueprint = blueprint.enrich()  # returns enriched blueprint object
>>> enriched_blueprint.publish()
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

Generated data dictionaries have to be manually filled for "source-rest" and "source-db" input types.

```
>>> blueprint.get_data_dictionaries().save_to_file("/tmp/dd.json")  # generate data dictionaries for blueprint and save it to "/tmp/dd.json" file
```

## Manage Blueprint Models in CDS

### Retrieve Blueprint Models from CDS 
 - All
```
>>> from onapsdk.cds import BlueprintModel
>>> all_blueprint_models = BlueprintModel.get_all()
```
 - Selected by **id** of Blueprint Model
``` 
>>> blueprint_model = BlueprintModel.get_by_id(blueprint_model_id='11111111-1111-1111-1111-111111111111')
>>> blueprint_model
BlueprintModel(artifact_name='test_name', blueprint_model_id='11111111-1111-1111-1111-111111111111')
```
- Selected by **name and version** of Blueprint Model
```
>>> blueprint_model = BlueprintModel.get_by_name_and_version(blueprint_name='test_name', blueprint_version='1.0.0')
>>> blueprint_model
BlueprintModel(artifact_name='test_name', blueprint_model_id='11111111-1111-1111-1111-111111111111')
```

### Delete Blueprint Model
``` 
>>> blueprint_model.delete()
```

### Download Blueprint Model 
``` 
>>> blueprint_model.save(dst_file_path='/tmp/blueprint.zip')
```

### Get Blueprint object for Blueprint Model
``` 
>>> blueprint = blueprint_model.get_blueprint()
```
After that, all operation for blueprint object, like execute blueprint workflow etc. can be executed.
